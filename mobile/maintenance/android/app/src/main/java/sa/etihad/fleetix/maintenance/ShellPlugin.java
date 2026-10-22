package sa.etihad.fleetix.maintenance;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "Shell")
public class ShellPlugin extends Plugin {

    static volatile boolean pageScrolled;
    private static final String PREFS = "fleetix_maintenance";
    private static final String URL_KEY = "server_url";

    static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    static String baseUrl(Context context) {
        if (!BuildConfig.BASE_URL.isEmpty()) {
            return BuildConfig.BASE_URL;
        }
        return prefs(context).getString(URL_KEY, null);
    }

    static void saveBaseUrl(Context context, String url) {
        prefs(context).edit().putString(URL_KEY, url).commit();
    }

    @PluginMethod
    public void settings(PluginCall call) {
        getActivity().startActivity(new Intent(getContext(), SettingsActivity.class));
        call.resolve();
    }

    @PluginMethod
    public void scrolled(PluginCall call) {
        pageScrolled = call.getBoolean("value", false);
        call.resolve();
    }
}
