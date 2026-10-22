package sa.etihad.fleetix.maintenance;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import org.json.JSONException;
import org.json.JSONObject;

final class AppVersion {

    static final String METHOD = "/api/method/fleetix.fleetix.api.maintenance.app_version";

    private AppVersion() {}

    static JSONObject fetch(String base) {
        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection) new URL(base + METHOD).openConnection();
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(10000);
            connection.setRequestProperty("Accept", "application/json");
            if (connection.getResponseCode() != HttpURLConnection.HTTP_OK) {
                return null;
            }
            try (InputStream in = connection.getInputStream()) {
                ByteArrayOutputStream out = new ByteArrayOutputStream();
                byte[] buffer = new byte[4096];
                int read;
                while ((read = in.read(buffer)) != -1) {
                    out.write(buffer, 0, read);
                }
                return new JSONObject(out.toString("UTF-8")).optJSONObject("message");
            }
        } catch (IOException | JSONException | RuntimeException e) {
            return null;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }
}
