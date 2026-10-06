package com.complycube.compat

import android.content.Intent
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity

/** Compiled instead of the SDK adapter. No SDK classes or SDK test sources are present. */
class SdkEntry(activity: ComponentActivity, panel: LinearLayout, state: TextView, intent: Intent) {
    init { state.text = "SDK-free control" }
}
