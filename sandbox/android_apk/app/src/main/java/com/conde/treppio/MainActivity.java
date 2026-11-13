package com.conde.treppio;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ComponentCallbacks2;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.HapticFeedbackConstants;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.ConsoleMessage;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.window.OnBackInvokedCallback;
import android.window.OnBackInvokedDispatcher;

import java.io.BufferedInputStream;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.zip.GZIPInputStream;

public class MainActivity extends Activity implements TextToSpeech.OnInitListener {

    private static final String VIRTUAL_HOST = "conde.treppio.local";
    private static final String VIRTUAL_ORIGIN = "https://" + VIRTUAL_HOST + "/";

    private WebView mWebView;
    private FrameLayout mRootLayout;
    private LinearLayout mSplashOverlay;
    private ImageView mSplashCrest;
    private volatile boolean mSplashDismissed = false;
    private TextToSpeech mTts;
    private boolean mTtsReady = false;
    private OnBackInvokedCallback mBackCallback;

    @Override
    @SuppressLint({"SetJavaScriptEnabled", "AddJavascriptInterface"})
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Estilização das barras de sistema (Obsidiana Soberana #09090b)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            Window window = getWindow();
            window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
            window.setStatusBarColor(Color.parseColor("#09090b"));
            window.setNavigationBarColor(Color.parseColor("#09090b"));
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                View decor = window.getDecorView();
                decor.setSystemUiVisibility(0);
            }
        }

        // Inicializar motor TextToSpeech nativo do Android para pronúncia Tréppia
        try {
            mTts = new TextToSpeech(this, this);
        } catch (Exception ignored) {
        }

        // Container raiz com WebView + Splash Overlay Nativo (Brasão Vetorizado & Obsidiana)
        mRootLayout = new FrameLayout(this);
        mRootLayout.setBackgroundColor(Color.parseColor("#09090b"));

        mWebView = new WebView(this);
        mWebView.setBackgroundColor(Color.parseColor("#09090b"));
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            mWebView.setRendererPriorityPolicy(WebView.RENDERER_PRIORITY_IMPORTANT, false);
        }
        mRootLayout.addView(mWebView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
        ));

        mSplashOverlay = buildImperialSplashOverlay();
        mRootLayout.addView(mSplashOverlay, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
        ));

        setContentView(mRootLayout);

        WebSettings settings = mWebView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(false);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setCacheMode(WebSettings.LOAD_NO_CACHE);

        // Registrar ponte JavaScript nativa (TTS, Clipboard, onUiReady)
        mWebView.addJavascriptInterface(new AndroidCondeBridge(), "AndroidCondeBridge");

        mWebView.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP || request == null || request.getUrl() == null) {
                    return super.shouldInterceptRequest(view, request);
                }
                Uri uri = request.getUrl();
                String host = uri.getHost();
                if (host != null && (host.equalsIgnoreCase("fonts.googleapis.com") || host.equalsIgnoreCase("fonts.gstatic.com"))) {
                    return new WebResourceResponse(
                            "text/css",
                            "UTF-8",
                            204,
                            "No Content",
                            null,
                            new ByteArrayInputStream(new byte[0])
                    );
                }
                if (VIRTUAL_HOST.equalsIgnoreCase(host)) {
                    return serveVirtualAsset(uri.getPath());
                }
                return super.shouldInterceptRequest(view, request);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                if (mWebView != null && !mSplashDismissed) {
                    mWebView.postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            dismissSplashOverlay();
                        }
                    }, 1200);
                }
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP && request != null) {
                    return handleUri(request.getUrl());
                }
                return false;
            }

            @SuppressWarnings("deprecation")
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return handleUri(Uri.parse(url));
            }

            private boolean handleUri(Uri uri) {
                if (uri == null) return false;
                String scheme = uri.getScheme();
                if (scheme != null && (scheme.equalsIgnoreCase("http") || scheme.equalsIgnoreCase("https"))) {
                    String host = uri.getHost();
                    if (host == null || (
                            !host.equalsIgnoreCase(VIRTUAL_HOST)
                            && !host.equalsIgnoreCase("127.0.0.1")
                            && !host.equalsIgnoreCase("localhost"))) {
                        try {
                            Intent intent = new Intent(Intent.ACTION_VIEW, uri);
                            startActivity(intent);
                            return true;
                        } catch (Exception e) {
                            return false;
                        }
                    }
                }
                return false;
            }
        });

        mWebView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage consoleMessage) {
                return super.onConsoleMessage(consoleMessage);
            }
        });

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            mBackCallback = new OnBackInvokedCallback() {
                @Override
                public void onBackInvoked() {
                    handleBackNavigation(new Runnable() {
                        @Override
                        public void run() {
                            finish();
                        }
                    });
                }
            };
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                    OnBackInvokedDispatcher.PRIORITY_DEFAULT,
                    mBackCallback
            );
        }

        // Carrega shell enxuto na origem virtual HTTPS segura sem engasgo
        mWebView.loadUrl(VIRTUAL_ORIGIN + "index.html");
    }

    private WebResourceResponse serveVirtualAsset(String rawPath) {
        String path = (rawPath == null || rawPath.isEmpty() || "/".equals(rawPath)) ? "index.html" : rawPath.substring(1);
        if (path.contains("..")) {
            return new WebResourceResponse("text/plain", "UTF-8", 403, "Forbidden", null, new ByteArrayInputStream(new byte[0]));
        }

        Map<String, String> headers = new HashMap<String, String>();
        headers.put("Access-Control-Allow-Origin", "*");
        headers.put("Cache-Control", "no-store");

        try {
            if ("dados_dicionario_conde.js".equals(path)) {
                InputStream jsStream;
                try {
                    // AAPT2 descompacta .js.gz no empacotamento para assets/dados_dicionario_conde.js (DEFLATE nativo no APK)
                    jsStream = new BufferedInputStream(getAssets().open("dados_dicionario_conde.js"), 32768);
                } catch (Exception missingPlain) {
                    InputStream gzRaw = getAssets().open("dados_dicionario_conde.js.gz");
                    jsStream = new BufferedInputStream(new GZIPInputStream(gzRaw, 32768), 32768);
                }
                return new WebResourceResponse("application/javascript", "UTF-8", 200, "OK", headers, jsStream);
            }

            InputStream assetStream = new BufferedInputStream(getAssets().open(path), 32768);
            String mime = "application/octet-stream";
            String encoding = null;
            if (path.endsWith(".html")) {
                mime = "text/html";
                encoding = "UTF-8";
            } else if (path.endsWith(".svg")) {
                mime = "image/svg+xml";
                encoding = "UTF-8";
            } else if (path.endsWith(".js")) {
                mime = "application/javascript";
                encoding = "UTF-8";
            } else if (path.endsWith(".png")) {
                mime = "image/png";
            } else if (path.endsWith(".ico")) {
                mime = "image/x-icon";
            } else if (path.endsWith(".json")) {
                mime = "application/json";
                encoding = "UTF-8";
            }
            return new WebResourceResponse(mime, encoding, 200, "OK", headers, assetStream);
        } catch (Exception e) {
            return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found", null, new ByteArrayInputStream(new byte[0]));
        }
    }

    private void dismissSplashOverlay() {
        if (mSplashDismissed || mSplashOverlay == null) return;
        mSplashDismissed = true;
        if (mSplashOverlay.getVisibility() == View.VISIBLE) {
            mSplashOverlay.animate()
                    .alpha(0f)
                    .setDuration(180)
                    .withEndAction(new Runnable() {
                        @Override
                        public void run() {
                            if (mSplashCrest != null) {
                                mSplashCrest.setImageDrawable(null);
                                mSplashCrest = null;
                            }
                            if (mSplashOverlay != null) {
                                mSplashOverlay.setVisibility(View.GONE);
                                mSplashOverlay.removeAllViews();
                                if (mRootLayout != null) {
                                    mRootLayout.removeView(mSplashOverlay);
                                }
                                mSplashOverlay = null;
                            }
                        }
                    })
                    .start();
        }
    }

    private LinearLayout buildImperialSplashOverlay() {
        LinearLayout splash = new LinearLayout(this);
        splash.setOrientation(LinearLayout.VERTICAL);
        splash.setGravity(Gravity.CENTER);
        splash.setBackgroundColor(Color.parseColor("#09090b"));
        int pad = dpToPx(32);
        splash.setPadding(pad, pad, pad, pad);

        mSplashCrest = new ImageView(this);
        mSplashCrest.setImageResource(R.drawable.brasao_conde_vector);
        mSplashCrest.setScaleType(ImageView.ScaleType.FIT_CENTER);
        LinearLayout.LayoutParams crestLp = new LinearLayout.LayoutParams(dpToPx(116), dpToPx(116));
        splash.addView(mSplashCrest, crestLp);

        TextView title = new TextView(this);
        title.setText("CÓDICE IMPERIAL TRÉPPIO");
        title.setTextColor(Color.parseColor("#fde28e"));
        title.setTextSize(TypedValue.COMPLEX_UNIT_SP, 18);
        title.setTypeface(Typeface.SERIF, Typeface.BOLD);
        title.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams titleLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        titleLp.topMargin = dpToPx(14);
        splash.addView(title, titleLp);

        TextView sub = new TextView(this);
        sub.setText("Era Clássica V9.0 • Brasão Vetorizado • 246.737 Formas");
        sub.setTextColor(Color.parseColor("#9da9c5"));
        sub.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
        sub.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams subLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        subLp.topMargin = dpToPx(6);
        splash.addView(sub, subLp);

        ProgressBar bar = new ProgressBar(this);
        LinearLayout.LayoutParams barLp = new LinearLayout.LayoutParams(dpToPx(36), dpToPx(36));
        barLp.topMargin = dpToPx(22);
        splash.addView(bar, barLp);

        return splash;
    }

    private int dpToPx(int dp) {
        return Math.round(dp * getResources().getDisplayMetrics().density);
    }

    private boolean mTtsPtBr = true;

    private String normalizeTreppioForTts(String text, boolean isPtBr) {
        if (text == null || text.isEmpty()) return "";
        String s = text.replace("'", " ");
        s = s.replace("y", "i").replace("Y", "I")
             .replace("ë", "ê").replace("Ë", "Ê");
        if (isPtBr) {
            s = java.util.regex.Pattern.compile("([gG]+)(?=[eéèêiíîEÉÈÊIÍÎ])")
                .matcher(s).replaceAll("$1u");
        } else {
            s = java.util.regex.Pattern.compile("([gG]+)(?=[eéèêiíîEÉÈÊIÍÎ])")
                .matcher(s).replaceAll("$1h");
        }
        s = java.util.regex.Pattern.compile("(?<=[aeiouáéíóúâêîôûàèìòùäïöüAEIOUÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÄÏÖÜ])s(?=[aeiouáéíóúâêîôûàèìòùäïöüAEIOUÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÄÏÖÜ])")
            .matcher(s).replaceAll("ss");
        s = java.util.regex.Pattern.compile("(?<=[aeiouáéíóúâêîôûàèìòùäïöüAEIOUÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÄÏÖÜ])S(?=[aeiouáéíóúâêîôûàèìòùäïöüAEIOUÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÄÏÖÜ])")
            .matcher(s).replaceAll("SS");
        return s;
    }

    @Override
    public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS && mTts != null) {
            int res = mTts.setLanguage(new Locale("pt", "BR"));
            mTtsPtBr = true;
            if (res == TextToSpeech.LANG_MISSING_DATA || res == TextToSpeech.LANG_NOT_SUPPORTED) {
                mTts.setLanguage(new Locale("it", "IT"));
                mTtsPtBr = false;
            }
            mTts.setSpeechRate(0.88f);
            mTtsReady = true;
        }
    }

    public class AndroidCondeBridge {
        @JavascriptInterface
        public void speak(final String text) {
            if (text == null || text.trim().isEmpty()) return;
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if (mWebView != null) {
                        mWebView.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
                    }
                    if (mTtsReady && mTts != null) {
                        String spoken = normalizeTreppioForTts(text, mTtsPtBr);
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                            mTts.speak(spoken, TextToSpeech.QUEUE_FLUSH, null, "conde_utt");
                        } else {
                            mTts.speak(spoken, TextToSpeech.QUEUE_FLUSH, null);
                        }
                    }
                }
            });
        }

        @JavascriptInterface
        public void onUiReady() {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    dismissSplashOverlay();
                }
            });
        }

        @JavascriptInterface
        public void copy(final String text) {
            if (text == null) return;
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        if (mWebView != null) {
                            mWebView.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS);
                        }
                        ClipboardManager cb = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                        if (cb != null) {
                            cb.setPrimaryClip(ClipData.newPlainText("Treppio", text));
                        }
                    } catch (Exception ignored) {
                    }
                }
            });
        }
    }

    private void handleBackNavigation(final Runnable fallbackExit) {
        if (mWebView == null) {
            fallbackExit.run();
            return;
        }
        mWebView.evaluateJavascript(
            "(function() {" +
            "  var m = document.getElementById('detail-modal');" +
            "  if (m && m.classList.contains('open')) {" +
            "    closeModal();" +
            "    return 'MODAL_CLOSED';" +
            "  }" +
            "  var search = document.getElementById('omni-input');" +
            "  if (search && search.value && search.value.length > 0) {" +
            "    clearSearch();" +
            "    return 'SEARCH_CLEARED';" +
            "  }" +
            "  return 'NORMAL';" +
            "})();",
            new ValueCallback<String>() {
                @Override
                public void onReceiveValue(String value) {
                    if (value != null && (value.contains("MODAL_CLOSED") || value.contains("SEARCH_CLEARED"))) {
                        return;
                    }
                    if (mWebView != null && mWebView.canGoBack()) {
                        mWebView.goBack();
                    } else {
                        fallbackExit.run();
                    }
                }
            }
        );
    }

    @SuppressWarnings("deprecation")
    @Override
    public void onBackPressed() {
        handleBackNavigation(new Runnable() {
            @Override
            public void run() {
                MainActivity.super.onBackPressed();
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (mWebView != null) {
            mWebView.onResume();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (mWebView != null) {
            mWebView.onPause();
        }
    }

    @Override
    public void onTrimMemory(int level) {
        super.onTrimMemory(level);
        if (level >= ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN && !isFinishing() && !isDestroyed()) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if (mWebView != null && !isFinishing() && !isDestroyed()) {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
                            mWebView.evaluateJavascript("if(window.__condeTrimMemory)window.__condeTrimMemory();", null);
                        }
                    }
                }
            });
        }
    }

    @Override
    protected void onDestroy() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU && mBackCallback != null) {
            try {
                getOnBackInvokedDispatcher().unregisterOnBackInvokedCallback(mBackCallback);
            } catch (Exception ignored) {
            }
        }
        if (mTts != null) {
            try {
                mTts.stop();
                mTts.shutdown();
            } catch (Exception ignored) {
            }
        }
        if (mWebView != null) {
            mWebView.destroy();
            mWebView = null;
        }
        mRootLayout = null;
        mSplashOverlay = null;
        mSplashCrest = null;
        super.onDestroy();
    }
}
