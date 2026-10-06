package com.complycube.compat

import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat

class HostActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        val panel = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        // Stable accessibility labels belong to this host, never to SDK internals.
        val state = TextView(this).apply { contentDescription = "host-state"; text = "Ready" }
        HostUi.add(this, panel)
        val networkState = TextView(this).apply { contentDescription = "network-state" }
        panel.addView(Button(this).apply {
            isAllCaps = false
            text = "Check host network"
            setOnClickListener {
                networkState.text = "Running"
                HostNetwork.run(intent.getStringExtra("fixtureUrl") ?: "") {
                    runOnUiThread { networkState.text = it }
                }
            }
        })
        panel.addView(networkState)
        SdkEntry(this, panel, state, intent)
        panel.addView(state)
        // targetSdk 35+ is drawn edge-to-edge. Without insets the first control sits under the
        // status bar, where it is neither tappable nor visible to UI Automator/accessibility.
        ViewCompat.setOnApplyWindowInsetsListener(panel) { view, insets ->
            val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout())
            view.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            insets
        }
        setContentView(panel)
    }
}
