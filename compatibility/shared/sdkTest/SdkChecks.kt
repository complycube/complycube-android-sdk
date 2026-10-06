package com.complycube.compat.tests

import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

/** Requires a reviewed synthetic remote workflow and fresh credentials for EACH entry. */
class SdkChecks : HostDriver() {
    @Test fun remoteWorkflowSelectorAndReturn() {
        val fixture = instrumentation.context.openFileInput("credentials.json").bufferedReader().use {
            JSONObject(it.readText())
        }
        val sessions = fixture.getJSONArray("sessions")
        assertEquals(2, sessions.length())
        LocalFixture().use { server ->
            repeat(2) { index ->
                val session = sessions.getJSONObject(index)
                launch(mapOf("fixtureUrl" to server.url,
                    "sdkToken" to session.getString("sdkToken"),
                    "clientId" to session.getString("clientId"),
                    "workflowTemplateId" to fixture.getString("workflowTemplateId")))
                val ktor = InstrumentationRegistry.getArguments().getString("family") == "ktor"
                awaitText("Host count 0").click()
                awaitText("Host count 1")
                if (ktor) network()
                awaitText("Open SDK").click()
                // This unique title exists only in the remote workflow, never in the app.
                // Loading it exercises SDK networking and response deserialization.
                awaitText(fixture.getString("remoteWelcomeTitle"))
                awaitText("Start verification").click() // SDK 1.7.2 resource verified in AAR.
                awaitText(fixture.getString("selectorOpenText")).click()
                awaitText(fixture.getString("selectorVisibleText"))
                device.pressBack()
                awaitText(fixture.getString("selectorOpenText"))
                device.pressBack()
                awaitText("Yes, cancel").click() // SDK 1.7.2 cancellation dialog resource.
                awaitText("SDK canceled") // Assert the documented SDK callback, not just activity exit.
                awaitText("Host count 1").click()
                awaitText("Host count 2")
                if (ktor) network()
            }
        }
    }
}
