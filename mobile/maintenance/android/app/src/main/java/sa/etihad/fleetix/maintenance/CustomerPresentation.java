package sa.etihad.fleetix.maintenance;

import android.app.Presentation;
import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.Display;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;
import com.getcapacitor.JSArray;
import org.json.JSONObject;

public class CustomerPresentation extends Presentation {

    private static final int INK = Color.parseColor("#0D1317");
    private static final int MUTED = Color.parseColor("#46515B");
    private static final int ACCENT = Color.parseColor("#F2A900");
    private LinearLayout root;

    public CustomerPresentation(Context outerContext, Display display) {
        super(outerContext, display);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        root = new LinearLayout(getContext());
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        root.setBackgroundColor(Color.WHITE);
        root.setPadding(48, 48, 48, 48);
        setContentView(root);
    }

    void render(String plate, String status, String title, JSArray rows) {
        root.removeAllViews();
        root.addView(text(plate, 96, INK, true));
        root.addView(text(status, 44, ACCENT, true));
        root.addView(text(title, 36, MUTED, true));
        for (int index = 0; index < rows.length(); index++) {
            JSONObject row = rows.optJSONObject(index);
            if (row != null) {
                root.addView(text(row.optString("label") + "  " + row.optString("value"), 34, INK, false));
            }
        }
    }

    private TextView text(String value, int size, int color, boolean bold) {
        TextView view = new TextView(getContext());
        view.setText(value);
        view.setTextSize(size);
        view.setTextColor(color);
        view.setGravity(Gravity.CENTER);
        view.setPadding(0, 12, 0, 12);
        if (bold) {
            view.setTypeface(Typeface.DEFAULT_BOLD);
        }
        return view;
    }
}
