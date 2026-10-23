package sa.etihad.fleetix.maintenance;

import android.webkit.JavascriptInterface;
import com.getcapacitor.Bridge;
import com.getcapacitor.JSExport;
import com.getcapacitor.PluginHandle;
import java.util.ArrayList;
import java.util.List;

final class PageBridge {

    static final String NAME = "FleetixBridge";
    private static final String[] PLUGINS = { "Shell", "CustomerDisplay", "SunmiPrinter" };

    private final String script;

    private PageBridge(String script) {
        this.script = script;
    }

    static PageBridge build(Bridge bridge) {
        List<PluginHandle> handles = new ArrayList<>();
        for (String id : PLUGINS) {
            PluginHandle handle = bridge.getPlugin(id);
            if (handle != null) {
                handles.add(handle);
            }
        }
        try {
            String script = JSExport.getGlobalJS(bridge.getContext(), bridge.getConfig().isLoggingEnabled(), bridge.isDevMode()) +
                "\n\nwindow.WEBVIEW_SERVER_URL = '" + bridge.getLocalUrl() + "';\n\n" +
                JSExport.getBridgeJS(bridge.getContext()) +
                "\n\n" +
                JSExport.getPluginJS(handles);
            return new PageBridge(script);
        } catch (Exception e) {
            return null;
        }
    }

    @JavascriptInterface
    public String script() {
        return script;
    }
}
