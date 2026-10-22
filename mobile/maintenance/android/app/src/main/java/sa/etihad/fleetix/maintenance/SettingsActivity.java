package sa.etihad.fleetix.maintenance;

import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.RemoteException;
import android.text.InputFilter;
import android.text.InputType;
import android.util.Base64;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import com.sunmi.peripheral.printer.InnerPrinterCallback;
import com.sunmi.peripheral.printer.InnerPrinterException;
import com.sunmi.peripheral.printer.InnerPrinterManager;
import com.sunmi.peripheral.printer.SunmiPrinterService;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.function.Consumer;

public class SettingsActivity extends AppCompatActivity {

    private static final String PIN_KEY = "pin_hash";
    private static final String SALT_KEY = "pin_salt";
    private final Handler handler = new Handler(Looper.getMainLooper());
    private LinearLayout column;
    private TextView message;
    private String firstPin;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(Color.parseColor("#F4F5F7"));
        scroll.setFillViewport(true);
        FrameLayout frame = new FrameLayout(this);
        column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        column.setBackgroundColor(Color.WHITE);
        column.setPadding(dp(40), dp(32), dp(40), dp(32));
        FrameLayout.LayoutParams card = new FrameLayout.LayoutParams(dp(560), ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.CENTER);
        card.setMargins(0, dp(24), 0, dp(24));
        frame.addView(column, card);
        scroll.addView(frame);
        setContentView(scroll);
        if (prefs().contains(PIN_KEY)) {
            askPin(R.string.pin_enter, this::checkPin);
        } else {
            askPin(R.string.pin_new, this::choosePin);
        }
    }

    private SharedPreferences prefs() {
        return ShellPlugin.prefs(this);
    }

    @Override
    protected void onResume() {
        super.onResume();
        ApkUpdater.resume(this);
    }

    private void askPin(int prompt, Consumer<String> next) {
        column.removeAllViews();
        column.addView(text(getString(prompt), 24, true));
        EditText input = field(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_VARIATION_PASSWORD);
        input.setFilters(new InputFilter[] { new InputFilter.LengthFilter(8) });
        input.setGravity(Gravity.CENTER);
        input.setOnEditorActionListener((view, action, event) -> {
            next.accept(input.getText().toString());
            return true;
        });
        column.addView(input);
        column.addView(button(R.string.ok, () -> next.accept(input.getText().toString())));
        column.addView(button(R.string.close, this::finish));
        message = text("", 18, false);
        message.setTextColor(Color.parseColor("#B3261E"));
        column.addView(message);
        input.requestFocus();
    }

    private void checkPin(String pin) {
        if (hash(pin).equals(prefs().getString(PIN_KEY, ""))) {
            showPanel();
        } else {
            message.setText(R.string.pin_wrong);
        }
    }

    private void choosePin(String pin) {
        if (!pin.matches("^[0-9]{4,8}$")) {
            message.setText(R.string.pin_short);
            return;
        }
        firstPin = pin;
        askPin(R.string.pin_repeat, this::confirmPin);
    }

    private void confirmPin(String pin) {
        if (!pin.equals(firstPin)) {
            firstPin = null;
            askPin(R.string.pin_new, this::choosePin);
            message.setText(R.string.pin_mismatch);
            return;
        }
        byte[] salt = new byte[16];
        new SecureRandom().nextBytes(salt);
        prefs().edit().putString(SALT_KEY, Base64.encodeToString(salt, Base64.NO_WRAP)).commit();
        prefs().edit().putString(PIN_KEY, hash(pin)).commit();
        showPanel();
    }

    private String hash(String pin) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            digest.update(prefs().getString(SALT_KEY, "").getBytes(StandardCharsets.UTF_8));
            return Base64.encodeToString(digest.digest(pin.getBytes(StandardCharsets.UTF_8)), Base64.NO_WRAP);
        } catch (NoSuchAlgorithmException e) {
            return "";
        }
    }

    private void showPanel() {
        column.removeAllViews();
        column.addView(text(getString(R.string.settings), 26, true));
        column.addView(text(getString(R.string.app_version) + "  " + BuildConfig.VERSION_NAME + " (" + BuildConfig.VERSION_CODE + ")", 18, false));
        if (BuildConfig.BASE_URL.isEmpty()) {
            column.addView(text(getString(R.string.server_address), 18, true));
            EditText url = field(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
            url.setTextDirection(TextView.TEXT_DIRECTION_LTR);
            String saved = ShellPlugin.baseUrl(this);
            url.setText(saved != null ? saved : "https://");
            column.addView(url);
            column.addView(button(R.string.save, () -> saveUrl(url.getText().toString())));
        }
        String base = ShellPlugin.baseUrl(this);
        if (base != null) {
            column.addView(button(R.string.update_check, () -> ApkUpdater.check(this, base, true)));
        }
        column.addView(button(R.string.printer_test, this::testPrinter));
        column.addView(button(R.string.close, this::finish));
        message = text("", 18, false);
        column.addView(message);
    }

    private void saveUrl(String raw) {
        String url = raw.trim().replaceAll("/+$", "");
        String pattern = BuildConfig.DEBUG ? "^https?://[A-Za-z0-9.-]+(:[0-9]{1,5})?$" : "^https://[A-Za-z0-9.-]+(:[0-9]{1,5})?$";
        if (!url.matches(pattern)) {
            message.setText(R.string.url_invalid);
            return;
        }
        message.setText(R.string.url_checking);
        new Thread(() -> {
            boolean reachable = AppVersion.fetch(url) != null;
            handler.post(() -> {
                if (!reachable) {
                    message.setText(R.string.url_unreachable);
                    return;
                }
                ShellPlugin.saveBaseUrl(this, url);
                restartShell();
            });
        }).start();
    }

    private void restartShell() {
        Intent intent = new Intent(this, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }

    private void testPrinter() {
        InnerPrinterCallback callback = new InnerPrinterCallback() {
            @Override
            protected void onConnected(SunmiPrinterService service) {
                int result;
                try {
                    int state = service.updatePrinterState();
                    result = printerMessage(state);
                    if (state == 1) {
                        service.printerInit(null);
                        service.printText(getString(R.string.printer_sample) + "\n" + getString(R.string.app_name) + " " + BuildConfig.VERSION_NAME + "\n", null);
                        service.lineWrap(3, null);
                    }
                } catch (RemoteException e) {
                    result = R.string.printer_error;
                }
                int shown = result;
                InnerPrinterCallback self = this;
                handler.post(() -> {
                    message.setText(shown);
                    try {
                        InnerPrinterManager.getInstance().unBindService(SettingsActivity.this, self);
                    } catch (InnerPrinterException ignored) {
                    }
                });
            }

            @Override
            protected void onDisconnected() {}
        };
        try {
            if (!InnerPrinterManager.getInstance().bindService(this, callback)) {
                message.setText(R.string.printer_missing);
            }
        } catch (InnerPrinterException e) {
            message.setText(R.string.printer_missing);
        }
    }

    private int printerMessage(int state) {
        switch (state) {
            case 1:
                return R.string.printer_ok;
            case 4:
                return R.string.printer_paper;
            case 5:
                return R.string.printer_hot;
            case 6:
                return R.string.printer_cover;
            case 505:
                return R.string.printer_missing;
            default:
                return R.string.printer_error;
        }
    }

    private TextView text(String value, int size, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(TypedValue.COMPLEX_UNIT_SP, size);
        view.setTextColor(MainActivity.INK);
        view.setPadding(0, dp(8), 0, dp(8));
        if (bold) {
            view.setTypeface(Typeface.DEFAULT_BOLD);
        }
        return view;
    }

    private EditText field(int type) {
        EditText input = new EditText(this);
        input.setInputType(type);
        input.setImeOptions(EditorInfo.IME_ACTION_DONE);
        input.setTextSize(TypedValue.COMPLEX_UNIT_SP, 22);
        input.setSingleLine(true);
        return input;
    }

    private Button button(int label, Runnable click) {
        Button view = new Button(this);
        view.setText(label);
        view.setTextSize(TypedValue.COMPLEX_UNIT_SP, 18);
        view.setOnClickListener(v -> click.run());
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56));
        params.setMargins(0, dp(8), 0, 0);
        view.setLayoutParams(params);
        return view;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
