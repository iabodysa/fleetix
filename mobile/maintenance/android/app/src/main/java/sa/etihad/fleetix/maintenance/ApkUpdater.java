package sa.etihad.fleetix.maintenance;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.core.content.FileProvider;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import org.json.JSONObject;

final class ApkUpdater {

    private static final String APK_TYPE = "application/vnd.android.package-archive";
    private static final Handler HANDLER = new Handler(Looper.getMainLooper());
    private static String pendingUrl;

    private ApkUpdater() {}

    static void check(Activity activity, String base, boolean manual) {
        new Thread(() -> {
            JSONObject latest = AppVersion.fetch(base);
            String url = latest == null || latest.isNull("url") ? "" : latest.optString("url");
            boolean newer = !url.isEmpty() && url.startsWith(base + "/") && latest.optInt("version_code") > BuildConfig.VERSION_CODE;
            HANDLER.post(() -> {
                if (activity.isFinishing()) {
                    return;
                }
                if (newer) {
                    offer(activity, latest.optString("version_name"), url);
                } else if (manual) {
                    Toast.makeText(activity, latest == null ? R.string.update_failed : R.string.update_none, Toast.LENGTH_LONG).show();
                }
            });
        }).start();
    }

    static void resume(Activity activity) {
        String url = pendingUrl;
        pendingUrl = null;
        if (url != null && canInstall(activity)) {
            download(activity, url);
        }
    }

    private static void offer(Activity activity, String name, String url) {
        new AlertDialog.Builder(activity)
            .setTitle(R.string.update_title)
            .setMessage(activity.getString(R.string.update_text).replace("{0}", name))
            .setPositiveButton(R.string.update_get, (dialog, which) -> install(activity, url))
            .setNegativeButton(R.string.cancel, null)
            .show();
    }

    private static boolean canInstall(Activity activity) {
        return Build.VERSION.SDK_INT < Build.VERSION_CODES.O || activity.getPackageManager().canRequestPackageInstalls();
    }

    private static void install(Activity activity, String url) {
        if (canInstall(activity)) {
            download(activity, url);
            return;
        }
        pendingUrl = url;
        activity.startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:" + activity.getPackageName())));
    }

    private static void download(Activity activity, String url) {
        ProgressBar bar = new ProgressBar(activity, null, android.R.attr.progressBarStyleHorizontal);
        bar.setIndeterminate(true);
        int pad = Math.round(24 * activity.getResources().getDisplayMetrics().density);
        bar.setPadding(pad, pad, pad, pad);
        AlertDialog dialog = new AlertDialog.Builder(activity)
            .setTitle(R.string.update_downloading)
            .setView(bar)
            .setCancelable(false)
            .show();
        File file = new File(new File(activity.getCacheDir(), "update"), "fleetix-maintenance.apk");
        new Thread(() -> {
            boolean saved = fetch(url, file, bar);
            HANDLER.post(() -> {
                dialog.dismiss();
                if (activity.isFinishing()) {
                    return;
                }
                if (!saved) {
                    Toast.makeText(activity, R.string.update_failed, Toast.LENGTH_LONG).show();
                    return;
                }
                Uri uri = FileProvider.getUriForFile(activity, activity.getPackageName() + ".fileprovider", file);
                Intent intent = new Intent(Intent.ACTION_VIEW)
                    .setDataAndType(uri, APK_TYPE)
                    .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
                activity.startActivity(intent);
            });
        }).start();
    }

    private static boolean fetch(String url, File file, ProgressBar bar) {
        HttpURLConnection connection = null;
        File dir = file.getParentFile();
        if (dir == null || (!dir.isDirectory() && !dir.mkdirs())) {
            return false;
        }
        try {
            connection = (HttpURLConnection) new URL(url).openConnection();
            connection.setConnectTimeout(15000);
            connection.setReadTimeout(30000);
            if (connection.getResponseCode() != HttpURLConnection.HTTP_OK) {
                return false;
            }
            long total = connection.getContentLengthLong();
            long done = 0;
            try (InputStream in = connection.getInputStream(); OutputStream out = new FileOutputStream(file)) {
                byte[] buffer = new byte[65536];
                int read;
                while ((read = in.read(buffer)) != -1) {
                    out.write(buffer, 0, read);
                    done += read;
                    if (total > 0) {
                        int percent = (int) (done * 100 / total);
                        HANDLER.post(() -> {
                            bar.setIndeterminate(false);
                            bar.setProgress(percent);
                        });
                    }
                }
            }
            return total <= 0 || done == total;
        } catch (IOException | RuntimeException e) {
            return false;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }
}
