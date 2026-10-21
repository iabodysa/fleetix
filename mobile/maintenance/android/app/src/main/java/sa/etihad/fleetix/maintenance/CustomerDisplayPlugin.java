package sa.etihad.fleetix.maintenance;

import android.content.Context;
import android.hardware.display.DisplayManager;
import android.view.Display;
import com.getcapacitor.JSArray;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "CustomerDisplay")
public class CustomerDisplayPlugin extends Plugin {

    private CustomerPresentation presentation;

    @PluginMethod
    public void show(PluginCall call) {
        String plate = call.getString("plate", "");
        String status = call.getString("status", "");
        String title = call.getString("title", "");
        JSArray rows = call.getArray("rows", new JSArray());
        getActivity().runOnUiThread(() -> {
            Display display = secondaryDisplay();
            if (display == null) {
                call.reject("NO_SECOND_DISPLAY");
                return;
            }
            if (presentation == null || presentation.getDisplay().getDisplayId() != display.getDisplayId()) {
                presentation = new CustomerPresentation(getActivity(), display);
                presentation.show();
            }
            presentation.render(plate, status, title, rows);
            call.resolve();
        });
    }

    @PluginMethod
    public void clear(PluginCall call) {
        getActivity().runOnUiThread(() -> {
            if (presentation != null) {
                presentation.dismiss();
                presentation = null;
            }
            call.resolve();
        });
    }

    @Override
    protected void handleOnDestroy() {
        if (presentation != null) {
            presentation.dismiss();
            presentation = null;
        }
    }

    private Display secondaryDisplay() {
        DisplayManager manager = (DisplayManager) getContext().getSystemService(Context.DISPLAY_SERVICE);
        Display[] displays = manager.getDisplays(DisplayManager.DISPLAY_CATEGORY_PRESENTATION);
        return displays.length > 0 ? displays[0] : null;
    }
}
