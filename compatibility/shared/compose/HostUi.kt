package com.complycube.compat

import android.widget.LinearLayout
import androidx.activity.ComponentActivity
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.ComposeView

object HostUi {
    fun add(activity: ComponentActivity, panel: LinearLayout) {
        panel.addView(ComposeView(activity).apply {
            setContent {
                var count by remember { mutableStateOf(0) }
                MaterialTheme {
                    Button(onClick = { count++ }) { Text("Host count $count") }
                }
            }
        })
    }
}
