package com.complycube.compat

import android.widget.Button
import android.widget.LinearLayout
import androidx.activity.ComponentActivity

object HostUi {
    fun add(activity: ComponentActivity, panel: LinearLayout) {
        panel.addView(Button(activity).apply {
            isAllCaps = false
            var count = 0
            text = "Host count 0"
            setOnClickListener { text = "Host count ${++count}" }
        })
    }
}
