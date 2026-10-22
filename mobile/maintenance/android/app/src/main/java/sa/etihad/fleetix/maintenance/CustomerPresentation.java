package sa.etihad.fleetix.maintenance;

import android.app.Presentation;
import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
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
        setContentView(root);
    }

    void idle() {
        root.removeAllViews();
        root.addView(lockup(0.42f));
        root.addView(text(getContext().getString(R.string.idle_welcome), 40, MainActivity.INK, true));
    }

    void step(String plate, String step) {
        root.removeAllViews();
        root.addView(lockup(0.2f));
        root.addView(text(plate, 88, MainActivity.INK, true));
        root.addView(text(step, 44, MainActivity.ACCENT, true));
    }

    void render(String plate, String status, String title, JSArray rows) {
        root.removeAllViews();
        root.addView(lockup(0.16f));
        root.addView(text(plate, 72, MainActivity.INK, true));
        root.addView(text(status, 36, MainActivity.ACCENT, true));
        root.addView(text(title, 30, MUTED, true));
        for (int index = 0; index < rows.length(); index++) {
            JSONObject row = rows.optJSONObject(index);
            if (row != null) {
                root.addView(text(row.optString("label") + "  " + row.optString("value"), 28, MainActivity.INK, false));
            }
        }
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
