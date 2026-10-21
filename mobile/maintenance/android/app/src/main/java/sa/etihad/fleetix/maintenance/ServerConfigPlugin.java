package sa.etihad.fleetix.maintenance;

import android.content.Context;
import android.content.SharedPreferences;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "ServerConfig")
public class ServerConfigPlugin extends Plugin {

    private static final String PREFS = "fleetix_maintenance";
    private static final String KEY = "server_url";

    static String savedUrl(Context context) {
        return prefs(context).getString(KEY, null);
    }

    private static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    @PluginMethod
    public void get(PluginCall call) {
        JSObject result = new JSObject();
        result.put("url", savedUrl(getContext()));
        call.resolve(result);
    }

    @PluginMethod
    public void set(PluginCall call) {
        String url = call.getString("url");
        if (url == null || !url.matches("^https?://[^/]+$")) {
            call.reject("INVALID_URL");
            return;
        }
        prefs(getContext()).edit().putString(KEY, url).commit();
        call.resolve();
        restart();
    }

    @PluginMethod
    public void reset(PluginCall call) {
        prefs(getContext()).edit().remove(KEY).commit();
        call.resolve();
        restart();
    }

    private void restart() {
        getActivity().runOnUiThread(() -> getActivity().recreate());
    }
}
