package sa.etihad.fleetix.maintenance;

import android.content.Context;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkInfo;
import android.net.Uri;
import android.net.http.SslError;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.SslErrorHandler;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.webkit.WebViewFeature;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.appcompat.app.AlertDialog;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;
import com.getcapacitor.Bridge;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.BridgeWebChromeClient;
import com.getcapacitor.BridgeWebViewClient;
import com.getcapacitor.CapConfig;
import java.net.CookieHandler;
import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends BridgeActivity {

    static final int INK = Color.parseColor("#0D1317");
    static final int ACCENT = Color.parseColor("#F2A900");
    private static final long TIMEOUT_MS = 30000;
    private static final long RETRY_MS = 10000;
    private static final int RETRY_STEPS = 3;
    private static final String ERROR_PAGE = "file:///android_asset/shell/error.html";
    private static final String SCROLL_PROBE =
        "(function(){if(window.__fleetixShell)return;window.__fleetixShell=1;" +
        "function up(node){for(var e=node;e&&e.nodeType===1;e=e.parentNode){if(e.scrollTop>0)return true}" +
        "var root=document.scrollingElement||document.documentElement;return root.scrollTop>0}" +
        "document.addEventListener('touchstart',function(ev){var p=window.Capacitor&&Capacitor.Plugins&&Capacitor.Plugins.Shell;" +
        "if(p)p.scrolled({value:up(ev.target)})},{capture:true,passive:true})})()";
    private static final String BACK_PROBE =
        "(function(){try{return !!(window.fleetixShell&&window.fleetixShell.back())}catch(e){return false}})()";
    private static boolean updateChecked;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable timeout = () -> fail("timeout", "", null);
    private final Runnable autoRetry = this::retry;
    private final Runnable autoHide = this::hideBar;
    private int retries;
    private WebView webView;
    private PageBridge pageBridge;
    private boolean nativePage;
    private boolean localPageInHistory;
    private WebView errorView;
    private SwipeRefreshLayout swipe;
    private View bar;
    private boolean edgePull;
    private boolean swallowGesture;
    private float pullStartY;
    private ProgressBar progress;
    private String baseUrl;
    private String startUrl;
    private String failedUrl;
    private String errorKind;
    private String errorCode;
    private boolean mainFrameFailed;
    private boolean loading;
    private ConnectivityManager.NetworkCallback networkCallback;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(ShellPlugin.class);
        registerPlugin(CustomerDisplayPlugin.class);
        baseUrl = ShellPlugin.baseUrl(this);
        nativePage = !WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT);
        if (baseUrl != null) {
            startUrl = baseUrl + "/maintenance";
            config = siteConfig(startUrl);
        }
        super.onCreate(savedInstanceState);
        CookieHandler.setDefault(null);
        if (baseUrl == null) {
            startActivity(new Intent(this, SettingsActivity.class));
            finish();
            return;
        }
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        webView = bridge.getWebView();
        CookieManager.getInstance().setAcceptCookie(true);
        bridge.setWebViewClient(new ShellClient(bridge));
        webView.setWebChromeClient(new ShellChromeClient(bridge));
        setContentView(buildLayout());
        watchNetwork();
        if (nativePage) {
            pageBridge = PageBridge.build(bridge);
            if (pageBridge != null) {
                webView.addJavascriptInterface(pageBridge, PageBridge.NAME);
            }
            localPageInHistory = true;
            webView.loadUrl(startUrl);
        }
    }

    @Override
    public void onPause() {
        super.onPause();
        CookieManager.getInstance().flush();
    }

    @Override
    public void onDestroy() {
        handler.removeCallbacksAndMessages(null);
        if (networkCallback != null) {
            connectivity().unregisterNetworkCallback(networkCallback);
        }
        super.onDestroy();
    }

    @Override
    public void onBackPressed() {
        if (webView == null) {
            super.onBackPressed();
            return;
        }
        back(true);
    }

    private CapConfig siteConfig(String url) {
        CapConfig bundled = CapConfig.loadDefault(this);
        JSONObject plugins = new JSONObject();
        try {
            plugins.put("SunmiPrinter", bundled.getPluginConfiguration("SunmiPrinter").getConfigJSON());
        } catch (JSONException ignored) {
            plugins = new JSONObject();
        }
        CapConfig.Builder builder = new CapConfig.Builder(this)
            .setAndroidScheme(bundled.getAndroidScheme())
            .setAllowMixedContent(bundled.isMixedContentAllowed())
            .setPluginsConfiguration(plugins);
        if (nativePage) {
            builder.setAllowNavigation(new String[] { Uri.parse(url).getHost() });
        } else {
            builder.setServerUrl(url);
        }
        return builder.create();
    }

    private View buildLayout() {
        ((ViewGroup) webView.getParent()).removeView(webView);
        FrameLayout frame = new FrameLayout(this);
        frame.setBackgroundColor(Color.WHITE);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        frame.addView(root, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        bar = toolbar();
        bar.setVisibility(View.GONE);
        frame.addView(bar, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56), Gravity.TOP));
        progress = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progress.setIndeterminate(true);
        progress.setIndeterminateTintList(ColorStateList.valueOf(ACCENT));
        progress.setVisibility(View.INVISIBLE);
        root.addView(progress, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(4)));
        FrameLayout body = new FrameLayout(this);
        swipe = new SwipeRefreshLayout(this);
        swipe.setColorSchemeColors(ACCENT);
        swipe.setOnChildScrollUpCallback((parent, child) -> ShellPlugin.pageScrolled);
        swipe.setOnRefreshListener(this::refresh);
        swipe.addView(webView, new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        body.addView(swipe, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        errorView = new WebView(this);
        errorView.getSettings().setJavaScriptEnabled(true);
        errorView.addJavascriptInterface(new ErrorActions(), "FleetixShellError");
        errorView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return true;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                renderError();
            }
        });
        errorView.setVisibility(View.GONE);
        errorView.loadUrl(ERROR_PAGE);
        body.addView(errorView, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        root.addView(body, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));
        return frame;
    }

    private View toolbar() {
        LinearLayout bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setBackgroundColor(INK);
        bar.setPadding(dp(8), 0, dp(8), 0);
        bar.addView(button(R.drawable.ic_back, R.string.back, v -> back(false)));
        bar.addView(button(R.drawable.ic_refresh, R.string.refresh, v -> refresh()));
        bar.addView(button(R.drawable.ic_home, R.string.home, v -> home()));
        TextView title = new TextView(this);
        title.setText(R.string.app_name);
        title.setTextColor(Color.WHITE);
        title.setTextSize(TypedValue.COMPLEX_UNIT_SP, 18);
        title.setGravity(Gravity.CENTER);
        bar.addView(title, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f));
        bar.addView(button(R.drawable.ic_settings, R.string.settings, v -> startActivity(new Intent(this, SettingsActivity.class))));
        return bar;
    }

    private TextView button(int icon, int label, View.OnClickListener click) {
        TextView view = new TextView(this);
        view.setText(label);
        view.setTextColor(Color.WHITE);
        view.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
        view.setGravity(Gravity.CENTER_VERTICAL);
        view.setCompoundDrawablesRelativeWithIntrinsicBounds(icon, 0, 0, 0);
        view.setCompoundDrawablePadding(dp(8));
        view.setPadding(dp(16), 0, dp(16), 0);
        TypedValue ripple = new TypedValue();
        getTheme().resolveAttribute(android.R.attr.selectableItemBackground, ripple, true);
        view.setBackgroundResource(ripple.resourceId);
        view.setClickable(true);
        view.setOnClickListener(click);
        view.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.MATCH_PARENT));
        return view;
    }

    private void back(boolean fromKey) {
        if (errorKind != null) {
            if (webView.canGoBack()) {
                hideError();
                webView.goBack();
            } else if (fromKey) {
                confirmExit();
            }
            return;
        }
        webView.evaluateJavascript(BACK_PROBE, value -> {
            if ("true".equals(value)) {
                return;
            }
            if (webView.canGoBack()) {
                webView.goBack();
            } else if (fromKey) {
                confirmExit();
            }
        });
    }

    private void refresh() {
        if (errorKind != null) {
            retry();
            return;
        }
        beginLoad();
        webView.reload();
    }

    private void home() {
        hideError();
        beginLoad();
        webView.loadUrl(startUrl);
    }

    private void retry() {
        String target = failedUrl != null ? failedUrl : startUrl;
        hideError();
        beginLoad();
        webView.loadUrl(target);
    }

    private void confirmExit() {
        new AlertDialog.Builder(this)
            .setTitle(R.string.exit_title)
            .setPositiveButton(R.string.exit_yes, (dialog, which) -> finish())
            .setNegativeButton(R.string.cancel, null)
            .show();
    }

    private void beginLoad() {
        progress.setVisibility(View.VISIBLE);
        if (!loading) {
            loading = true;
            handler.removeCallbacks(timeout);
            handler.postDelayed(timeout, TIMEOUT_MS);
        }
    }

    private void endLoad() {
        loading = false;
        handler.removeCallbacks(timeout);
        progress.setVisibility(View.INVISIBLE);
        swipe.setRefreshing(false);
    }

    private void fail(String kind, String code, String url) {
        endLoad();
        if ("timeout".equals(kind)) {
            webView.stopLoading();
        }
        mainFrameFailed = true;
        errorKind = online() ? kind : "offline";
        errorCode = code;
        String target = url != null ? url : webView.getUrl();
        if (target != null && target.startsWith(baseUrl)) {
            failedUrl = target;
        }
        errorView.setVisibility(View.VISIBLE);
        renderError();
        boolean passing = "timeout".equals(errorKind) || "unreachable".equals(errorKind) || code.startsWith("HTTP 5");
        handler.removeCallbacks(autoRetry);
        if (passing) {
            handler.postDelayed(autoRetry, RETRY_MS << retries);
            retries = Math.min(retries + 1, RETRY_STEPS);
        }
    }

    private void hideError() {
        handler.removeCallbacks(autoRetry);
        errorKind = null;
        errorView.setVisibility(View.GONE);
    }

    private void renderError() {
        if (errorKind == null) {
            return;
        }
        int title = R.string.error_server_title;
        int text = R.string.error_server_text;
        if ("offline".equals(errorKind)) {
            title = R.string.error_offline_title;
            text = R.string.error_offline_text;
        } else if ("ssl".equals(errorKind)) {
            title = R.string.error_ssl_title;
            text = R.string.error_ssl_text;
        } else if ("timeout".equals(errorKind)) {
            title = R.string.error_timeout_title;
            text = R.string.error_timeout_text;
        } else if ("unreachable".equals(errorKind)) {
            title = R.string.error_unreachable_title;
            text = R.string.error_unreachable_text;
        }
        JSONObject state = new JSONObject();
        try {
            boolean rtl = getResources().getConfiguration().getLayoutDirection() == View.LAYOUT_DIRECTION_RTL;
            state.put("dir", rtl ? "rtl" : "ltr");
            state.put("title", getString(title));
            state.put("text", getString(text));
            state.put("code", errorCode);
            state.put("retry", getString(R.string.retry));
            state.put("home", getString(R.string.home));
        } catch (JSONException e) {
            return;
        }
        errorView.evaluateJavascript("typeof show==='function'&&show(" + state + ")", null);
    }

    private String kindFor(int code) {
        if (code == WebViewClient.ERROR_TIMEOUT) {
            return "timeout";
        }
        if (code == WebViewClient.ERROR_FAILED_SSL_HANDSHAKE) {
            return "ssl";
        }
        if (code == WebViewClient.ERROR_HOST_LOOKUP || code == WebViewClient.ERROR_CONNECT) {
            return "unreachable";
        }
        return "server";
    }

    private ConnectivityManager connectivity() {
        return (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
    }

    private boolean online() {
        NetworkInfo info = connectivity().getActiveNetworkInfo();
        return info != null && info.isConnected();
    }

    private void watchNetwork() {
        networkCallback = new ConnectivityManager.NetworkCallback() {
            @Override
            public void onAvailable(Network network) {
                handler.postDelayed(() -> {
                    if ("offline".equals(errorKind)) {
                        retry();
                    }
                }, 1500);
            }
        };
        connectivity().registerDefaultNetworkCallback(networkCallback);
    }

    private void checkUpdate() {
        if (updateChecked) {
            return;
        }
        updateChecked = true;
        ApkUpdater.check(this, baseUrl, false);
    }

    @Override
    public void onResume() {
        super.onResume();
        immersive();
        ApkUpdater.resume(this);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            immersive();
        }
    }

    private void immersive() {
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        WindowInsetsControllerCompat controller = WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView());
        controller.setSystemBarsBehavior(WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
        controller.hide(WindowInsetsCompat.Type.systemBars());
    }

    @Override
    public boolean dispatchTouchEvent(MotionEvent event) {
        if (bar == null) {
            return super.dispatchTouchEvent(event);
        }
        int action = event.getActionMasked();
        if (action == MotionEvent.ACTION_DOWN) {
            edgePull = false;
            swallowGesture = bar.getVisibility() == View.VISIBLE && event.getY() > bar.getBottom();
            if (swallowGesture) {
                hideBar();
                return true;
            }
            edgePull = event.getY() < dp(32);
            pullStartY = event.getY();
        } else if (action == MotionEvent.ACTION_MOVE && edgePull && event.getY() - pullStartY > dp(48)) {
            edgePull = false;
            swallowGesture = true;
            showBar();
            MotionEvent cancel = MotionEvent.obtain(event);
            cancel.setAction(MotionEvent.ACTION_CANCEL);
            super.dispatchTouchEvent(cancel);
            cancel.recycle();
            return true;
        }
        if (swallowGesture) {
            if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                swallowGesture = false;
            }
            return true;
        }
        return super.dispatchTouchEvent(event);
    }

    private void showBar() {
        bar.setVisibility(View.VISIBLE);
        handler.removeCallbacks(autoHide);
        handler.postDelayed(autoHide, 5000);
    }

    private void hideBar() {
        handler.removeCallbacks(autoHide);
        bar.setVisibility(View.GONE);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private class ShellClient extends BridgeWebViewClient {

        ShellClient(Bridge bridge) {
            super(bridge);
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            boolean handled = super.shouldOverrideUrlLoading(view, request);
            if (!handled && request.isForMainFrame()) {
                beginLoad();
            }
            return handled;
        }

        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
            if (nativePage && request.isForMainFrame() && "GET".equals(request.getMethod())) {
                return null;
            }
            return super.shouldInterceptRequest(view, request);
        }

        @Override
        public void onPageStarted(WebView view, String url, Bitmap favicon) {
            super.onPageStarted(view, url, favicon);
            mainFrameFailed = false;
            ShellPlugin.pageScrolled = false;
            beginLoad();
        }

        @Override
        public void onPageFinished(WebView view, String url) {
            super.onPageFinished(view, url);
            endLoad();
            CookieManager.getInstance().flush();
            if (mainFrameFailed) {
                return;
            }
            retries = 0;
            if (localPageInHistory && url.startsWith(baseUrl)) {
                localPageInHistory = false;
                view.clearHistory();
            }
            view.evaluateJavascript(SCROLL_PROBE, null);
            checkUpdate();
        }

        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            super.onReceivedError(view, request, error);
            if (request.isForMainFrame() && errorKind == null) {
                fail(kindFor(error.getErrorCode()), "", request.getUrl().toString());
            }
        }

        @Override
        public void onReceivedHttpError(WebView view, WebResourceRequest request, WebResourceResponse response) {
            super.onReceivedHttpError(view, request, response);
            if (request.isForMainFrame() && errorKind == null && response.getStatusCode() >= 400) {
                fail("server", "HTTP " + response.getStatusCode(), request.getUrl().toString());
            }
        }

        @Override
        public void onReceivedSslError(WebView view, SslErrorHandler sslHandler, SslError error) {
            sslHandler.cancel();
            fail("ssl", "SSL " + error.getPrimaryError(), error.getUrl());
        }
    }

    private class ShellChromeClient extends BridgeWebChromeClient {

        ShellChromeClient(Bridge bridge) {
            super(bridge);
        }

        @Override
        public void onProgressChanged(WebView view, int newProgress) {
            super.onProgressChanged(view, newProgress);
            if (newProgress < 100) {
                beginLoad();
            }
        }
    }

    private class ErrorActions {

        @JavascriptInterface
        public void retry() {
            handler.post(MainActivity.this::retry);
        }

        @JavascriptInterface
        public void home() {
            handler.post(MainActivity.this::home);
        }
    }
}
