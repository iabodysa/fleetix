package sa.etihad.fleetix.maintenance;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.CapConfig;
import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(ServerConfigPlugin.class);
        registerPlugin(CustomerDisplayPlugin.class);
        String url = ServerConfigPlugin.savedUrl(this);
        if (url != null) {
            config = siteConfig(url);
        }
        super.onCreate(savedInstanceState);
    }

    private CapConfig siteConfig(String url) {
        CapConfig bundled = CapConfig.loadDefault(this);
        JSONObject plugins = new JSONObject();
        try {
            plugins.put("SunmiPrinter", bundled.getPluginConfiguration("SunmiPrinter").getConfigJSON());
        } catch (JSONException ignored) {
            plugins = new JSONObject();
        }
        return new CapConfig.Builder(this)
            .setServerUrl(url + "/maintenance")
            .setAndroidScheme(bundled.getAndroidScheme())
            .setAllowMixedContent(bundled.isMixedContentAllowed())
            .setPluginsConfiguration(plugins)
            .create();
    }
}
