package com.complycube.compat

import android.content.Intent
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import com.complycube.sdk.ComplyCubeSdk
import com.complycube.sdk.common.data.ClientAuth
import com.complycube.sdk.common.data.Result

class SdkEntry(activity: ComponentActivity, panel: LinearLayout, state: TextView, intent: Intent) {
    init {
        val builder = ComplyCubeSdk.Builder(activity) { result ->
            state.text = when (result) {
                is Result.Canceled -> "SDK canceled"
                is Result.Success -> "SDK success"
                is Result.Error -> "SDK error"
                else -> "SDK no result"
            }
        }
        panel.addView(Button(activity).apply {
            isAllCaps = false
            text = "Open SDK"
            setOnClickListener {
                // Runtime-only extras supplied by the private instrumentation fixture.
                val token = intent.getStringExtra("sdkToken")
                val client = intent.getStringExtra("clientId")
                val template = intent.getStringExtra("workflowTemplateId")
                if (token.isNullOrEmpty() || client.isNullOrEmpty() || template.isNullOrEmpty()) {
                    state.text = "BLOCKED: fresh SDK token, client and workflow template required"
                } else {
                    builder.withWorkflowTemplateId(template)
                    builder.start(ClientAuth(token = token, clientId = client))
                }
            }
        })
    }
}
