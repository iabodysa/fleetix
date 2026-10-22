package sa.etihad.fleetix.maintenance;

import android.content.Context;
import android.hardware.display.DisplayManager;
import android.os.Handler;
import android.os.Looper;
import android.view.Display;
import com.getcapacitor.JSArray;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "CustomerDisplay")
public class CustomerDisplayPlugin extends Plugin {

    private CustomerPresentation presentation;
    private DisplayManager displays;
    private final DisplayManager.DisplayListener listener = new DisplayManager.DisplayListener() {
        @Override
        public void onDisplayAdded(int displayId) {
            idleIfAbsent();
        }

        @Override
        public void onDisplayRemoved(int displayId) {
            if (presentation != null && presentation.getDisplay().getDisplayId() == displayId) {
                presentation.dismiss();
                presentation = null;
            }
        }

        @Override
        public void onDisplayChanged(int displayId) {}
    };

    @Override
    public void load() {
        displays = (DisplayManager) getContext().getSystemService(Context.DISPLAY_SERVICE);
        displays.registerDisplayListener(listener, new Handler(Looper.getMainLooper()));
        getActivity().runOnUiThread(this::idleIfAbsent);
    }

    @PluginMethod
    public void show(PluginCall call) {
        String plate = call.getString("plate", "");
        String status = call.getString("status", "");
        String title = call.getString("title", "");
        JSArray rows = call.getArray("rows", new JSArray());
        getActivity().runOnUiThread(() -> {
            if (!ensure()) {
                call.reject("NO_SECOND_DISPLAY");
                return;
            }
            presentation.render(plate, status, title, rows);
            call.resolve();
        });
    }

    @PluginMethod
    public void step(PluginCall call) {
        String plate = call.getString("plate", "");
        String step = call.getString("step", "");
        getActivity().runOnUiThread(() -> {
            if (!ensure()) {
                call.reject("NO_SECOND_DISPLAY");
                return;
            }
            presentation.step(plate, step);
            call.resolve();
        });
    }

    @PluginMethod
    public void idle(PluginCall call) {
        getActivity().runOnUiThread(() -> {
            if (!ensure()) {
                call.reject("NO_SECOND_DISPLAY");
                return;
            }
            presentation.idle();
            call.resolve();
        });
    }

    @Override
    protected void handleOnDestroy() {
        displays.unregisterDisplayListener(listener);
        if (presentation != null) {
            presentation.dismiss();
            presentation = null;
        }
    }

    private void idleIfAbsent() {
        if (presentation == null && ensure()) {
            presentation.idle();
        }
    }

    private boolean ensure() {
        Display[] found = displays.getDisplays(DisplayManager.DISPLAY_CATEGORY_PRESENTATION);
        if (found.length == 0 || getActivity().isFinishing()) {
            return false;
        }
        Display display = found[0];
        if (presentation == null || presentation.getDisplay().getDisplayId() != display.getDisplayId()) {
            if (presentation != null) {
                presentation.dismiss();
            }
            presentation = new CustomerPresentation(getActivity(), display);
            presentation.show();
        }
        return true;
    }
}
