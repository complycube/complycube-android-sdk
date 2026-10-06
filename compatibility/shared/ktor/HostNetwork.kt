package com.complycube.compat

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.engine.android.Android
import io.ktor.client.plugins.ClientRequestException
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.get
import io.ktor.http.HttpStatusCode
import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonPrimitive

/** Executed inside the application, including under R8. The fixture is a real HTTP server. */
object HostNetwork {
    fun run(baseUrl: String, report: (String) -> Unit) {
        Thread {
            try {
                require(baseUrl.startsWith("http://127.0.0.1:"))
                runBlocking {
                    val client = HttpClient(Android) {
                        expectSuccess = true
                        install(ContentNegotiation) { json() }
                    }
                    try {
                        val body: JsonObject = client.get("$baseUrl/success").body()
                        check(body["message"]?.jsonPrimitive?.content == "synthetic-fixture")
                        try {
                            client.get("$baseUrl/error")
                            error("Expected HTTP error")
                        } catch (error: ClientRequestException) {
                            check(error.response.status == HttpStatusCode.BadRequest)
                        }
                        try {
                            withTimeout(250) { client.get("$baseUrl/slow").body<JsonObject>() }
                            error("Expected cancellation")
                        } catch (_: TimeoutCancellationException) { }
                        // A canceled request must not poison the client.
                        check(client.get("$baseUrl/success").body<JsonObject>()["message"]?.jsonPrimitive?.content == "synthetic-fixture")
                    } finally { client.close() }
                }
                report("Network PASS: success error cancellation recovery")
            } catch (error: Throwable) {
                // No URLs, response bodies, tokens, or SDK result objects in public logs.
                report("Network FAIL: ${error.javaClass.name}")
            }
        }.start()
    }
}
