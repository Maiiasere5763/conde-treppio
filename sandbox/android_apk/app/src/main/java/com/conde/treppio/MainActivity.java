package com.conde.treppio;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
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
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

import java.util.Locale;

public class MainActivity extends Activity implements TextToSpeech.OnInitListener {

    private WebView mWebView;
    private LinearLayout mSplashOverlay;
    private TextToSpeech mTts;
    private boolean mTtsReady = false;

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

        // Container raiz com WebView + Splash Overlay Nativo (Ouro Imperial & Obsidiana)
        FrameLayout rootLayout = new FrameLayout(this);
        rootLayout.setBackgroundColor(Color.parseColor("#09090b"));

        mWebView = new WebView(this);
        mWebView.setBackgroundColor(Color.parseColor("#09090b"));
        rootLayout.addView(mWebView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
        ));

        mSplashOverlay = buildImperialSplashOverlay();
        rootLayout.addView(mSplashOverlay, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
        ));

        setContentView(rootLayout);

        WebSettings settings = mWebView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN) {
            settings.setAllowFileAccessFromFileURLs(true);
            settings.setAllowUniversalAccessFromFileURLs(true);
        }

        // Registrar ponte JavaScript nativa para síntese de voz (TTS) e área de transferência
        mWebView.addJavascriptInterface(new AndroidCondeBridge(), "AndroidCondeBridge");

        mWebView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                if (mSplashOverlay != null && mSplashOverlay.getVisibility() == View.VISIBLE) {
                    mSplashOverlay.animate()
                            .alpha(0f)
                            .setDuration(300)
                            .withEndAction(new Runnable() {
                                @Override
                                public void run() {
                                    mSplashOverlay.setVisibility(View.GONE);
                                }
                            })
                            .start();
                }
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    return handleUri(request.getUrl());
                }
                return false;
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return handleUri(Uri.parse(url));
            }

            private boolean handleUri(Uri uri) {
                String scheme = uri.getScheme();
                if (scheme != null && (scheme.equalsIgnoreCase("http") || scheme.equalsIgnoreCase("https"))) {
                    if (!uri.toString().contains("127.0.0.1") && !uri.toString().contains("localhost")) {
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

        // Carregar o Códice V8.4 autocontido dos assets locais
        mWebView.loadUrl("file:///android_asset/index.html");
    }

    private LinearLayout buildImperialSplashOverlay() {
        LinearLayout splash = new LinearLayout(this);
        splash.setOrientation(LinearLayout.VERTICAL);
        splash.setGravity(Gravity.CENTER);
        splash.setBackgroundColor(Color.parseColor("#09090b"));
        int pad = dpToPx(32);
        splash.setPadding(pad, pad, pad, pad);

        TextView crest = new TextView(this);
        crest.setText("𝓣");
        crest.setTextColor(Color.parseColor("#fde28e"));
        crest.setTextSize(TypedValue.COMPLEX_UNIT_SP, 48);
        crest.setTypeface(Typeface.SERIF, Typeface.BOLD);
        crest.setGravity(Gravity.CENTER);
        splash.addView(crest);

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
        titleLp.topMargin = dpToPx(12);
        splash.addView(title, titleLp);

        TextView sub = new TextView(this);
        sub.setText("Era Clássica V8.4 • 246.737 Formas Validadas");
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
        barLp.topMargin = dpToPx(24);
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

    @Override
    public void onBackPressed() {
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
                    if (mWebView.canGoBack()) {
                        mWebView.goBack();
                    } else {
                        MainActivity.super.onBackPressed();
                    }
                }
            }
        );
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
    protected void onDestroy() {
        if (mTts != null) {
            try {
                mTts.stop();
                mTts.shutdown();
            } catch (Exception ignored) {
            }
        }
        if (mWebView != null) {
            mWebView.destroy();
        }
        super.onDestroy();
    }
}
