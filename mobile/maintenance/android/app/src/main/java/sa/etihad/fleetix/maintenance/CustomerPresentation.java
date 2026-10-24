package sa.etihad.fleetix.maintenance;

import android.app.Presentation;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.BitmapDrawable;
import android.os.Bundle;
import android.util.TypedValue;
import android.view.Display;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import com.getcapacitor.JSArray;
import org.json.JSONObject;

public class CustomerPresentation extends Presentation {

    private static final int MUTED = Color.parseColor("#46515B");
    private LinearLayout root;
    private Bitmap qr;
    private String cardPlate = "";
    private String delegate = "";
    private boolean zoomed;
    private Runnable redraw = () -> {};

    public CustomerPresentation(Context outerContext, Display display) {
        super(outerContext, display);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        root = new LinearLayout(getContext());
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setLayoutDirection(View.LAYOUT_DIRECTION_LOCALE);
        root.setBackgroundColor(Color.WHITE);
        root.setPadding(dp(32), dp(24), dp(32), dp(24));
        root.setOnClickListener(view -> {
            if (qr != null) {
                zoomed = !zoomed;
                redraw.run();
            }
        });
        setContentView(root);
    }

    private interface Body {
        void fill(LinearLayout column);
    }

    void idle() {
        qr = null;
        cardPlate = "";
        zoomed = false;
        redraw = () -> {
            root.removeAllViews();
            root.setOrientation(LinearLayout.VERTICAL);
            root.addView(lockup(0.42f));
            root.addView(text(getContext().getString(R.string.idle_welcome), 40, MainActivity.INK, true));
            root.addView(text(getContext().getString(R.string.idle_track), 26, MUTED, false));
        };
        redraw.run();
    }

    void step(String plate, String step, String delegate, JSArray rows) {
        keepCard(plate, delegate, rows);
        redraw = () -> drawCard(column -> {
            column.addView(text(plate, 88, MainActivity.INK, true));
            column.addView(text(step, 44, MainActivity.ACCENT, true));
        });
        redraw.run();
    }

    void render(String plate, String status, String title, JSArray rows) {
        if (!plate.equals(cardPlate)) {
            keepCard(plate, "", new JSArray());
        }
        redraw = () -> drawCard(column -> {
            column.addView(text(plate, 72, MainActivity.INK, true));
            column.addView(text(status, 36, MainActivity.ACCENT, true));
            column.addView(text(title, 30, MUTED, true));
            for (int index = 0; index < rows.length(); index++) {
                JSONObject row = rows.optJSONObject(index);
                if (row != null) {
                    column.addView(text(row.optString("label") + "  " + row.optString("value"), 28, MainActivity.INK, false));
                }
            }
        });
        redraw.run();
    }

    private void keepCard(String plate, String delegate, JSArray rows) {
        if (!plate.equals(cardPlate)) {
            zoomed = false;
        }
        cardPlate = plate;
        this.delegate = delegate;
        qr = rows.length() == 0 ? null : matrix(rows);
    }

    private void drawCard(Body body) {
        root.removeAllViews();
        root.setOrientation(zoomed && qr != null ? LinearLayout.VERTICAL : LinearLayout.HORIZONTAL);
        if (zoomed && qr != null) {
            root.addView(qrView(0.78f));
            root.addView(text(getContext().getString(R.string.idle_track), 32, MainActivity.INK, true));
            return;
        }
        LinearLayout column = new LinearLayout(getContext());
        column.setOrientation(LinearLayout.VERTICAL);
        column.setGravity(Gravity.CENTER);
        column.setLayoutParams(new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f));
        column.addView(lockup(0.16f));
        body.fill(column);
        if (!delegate.isEmpty()) {
            column.addView(text(delegate, 30, MUTED, false));
        }
        root.addView(column);
        if (qr == null) {
            return;
        }
        LinearLayout side = new LinearLayout(getContext());
        side.setOrientation(LinearLayout.VERTICAL);
        side.setGravity(Gravity.CENTER);
        side.addView(qrView(0.6f));
        side.addView(text(getContext().getString(R.string.idle_track), 24, MUTED, true));
        root.addView(side);
    }

    private Bitmap matrix(JSArray rows) {
        int size = rows.length();
        Bitmap bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888);
        for (int y = 0; y < size; y++) {
            String line = rows.optString(y);
            for (int x = 0; x < size; x++) {
                bitmap.setPixel(x, y, x < line.length() && line.charAt(x) == '1' ? Color.BLACK : Color.WHITE);
            }
        }
        return bitmap;
    }

    private ImageView qrView(float share) {
        int modules = qr.getWidth();
        int side = Math.round(getContext().getResources().getDisplayMetrics().heightPixels * share);
        int scale = Math.max(1, side / modules);
        BitmapDrawable drawable = new BitmapDrawable(
            getContext().getResources(), Bitmap.createScaledBitmap(qr, modules * scale, modules * scale, false)
        );
        drawable.setFilterBitmap(false);
        ImageView view = new ImageView(getContext());
        view.setImageDrawable(drawable);
        view.setScaleType(ImageView.ScaleType.CENTER);
        view.setLayoutParams(new LinearLayout.LayoutParams(modules * scale, modules * scale));
        return view;
    }

    private ImageView lockup(float share) {
        ImageView view = new ImageView(getContext());
        view.setImageResource(R.drawable.etihad_lockup);
        view.setAdjustViewBounds(true);
        view.setScaleType(ImageView.ScaleType.FIT_CENTER);
        int height = Math.round(getContext().getResources().getDisplayMetrics().heightPixels * share);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, height);
        params.gravity = Gravity.CENTER_HORIZONTAL;
        params.bottomMargin = dp(16);
        view.setLayoutParams(params);
        return view;
    }

    private TextView text(String value, int size, int color, boolean bold) {
        TextView view = new TextView(getContext());
        view.setText(value);
        view.setTextSize(TypedValue.COMPLEX_UNIT_SP, size);
        view.setTextColor(color);
        view.setGravity(Gravity.CENTER);
        view.setPadding(0, dp(6), 0, dp(6));
        if (bold) {
            view.setTypeface(Typeface.DEFAULT_BOLD);
        }
        return view;
    }

    private int dp(int value) {
        return Math.round(value * getContext().getResources().getDisplayMetrics().density);
    }
}
