package com.complycube.compat.tests

import android.content.Intent
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.By
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.Until
import org.junit.Assert.*
import org.junit.After
import org.junit.Test
import java.net.InetAddress
import java.net.ServerSocket
import java.util.Collections
import kotlin.concurrent.thread

private const val HOST = "com.complycube.compat"

/**
 * Runs in the separate driver APK and process. It never loads host classes, so
 * R8 output is exercised exactly as shipped. Explicit Intent extras are the only
 * input channel; UI Automator text is the only observation channel.
 */
open class HostDriver {
    protected val instrumentation = InstrumentationRegistry.getInstrumentation()
    protected val device = UiDevice.getInstance(instrumentation)

    /** CLEAR_TASK replaces any earlier host activity but keeps a warm process, like a real re-entry. */
    protected fun launch(extras: Map<String, String> = emptyMap()) {
        device.wakeUp()
        val intent = Intent().setClassName(HOST, "$HOST.HostActivity")
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
        extras.forEach { (key, value) -> intent.putExtra(key, value) }
        instrumentation.context.startActivity(intent)
        check(device.wait(Until.hasObject(By.pkg(HOST)), 30_000)) {
            "Host activity did not reach the foreground"
        }
        awaitText("Host count 0")
    }

    @After fun stopHost() {
        device.executeShellCommand("am force-stop $HOST")
    }

    protected fun awaitText(text: String) = requireNotNull(device.wait(Until.findObject(By.text(text)), 30_000)) {
        // Only known synthetic UI labels, never dump the UI hierarchy.
        "Expected fixture UI was not visible"
    }
    protected fun network() {
        awaitText("Check host network").click()
        awaitText("Network PASS: success error cancellation recovery")
    }
}

class HostChecks : HostDriver() {
    @Test fun hostContract() {
        LocalFixture().use { fixture ->
            launch(mapOf("fixtureUrl" to fixture.url))
            awaitText("Host count 0").click()
            awaitText("Host count 1").click()
            awaitText("Host count 2")
            if (InstrumentationRegistry.getArguments().getString("family") == "ktor") {
                network()
                assertTrue(fixture.paths.containsAll(listOf("/success", "/error", "/slow")))
                assertTrue(fixture.paths.count { it == "/success" } >= 2)
            }
        }
    }
}

/** Loopback only; success, HTTP 400, and a cancellable delayed response. No MockEngine. */
class LocalFixture : java.io.Closeable {
    private val server = ServerSocket(0, 10, InetAddress.getByName("127.0.0.1"))
    val paths: MutableList<String> = Collections.synchronizedList(mutableListOf())
    val url = "http://127.0.0.1:${server.localPort}"
    private val sockets = Collections.synchronizedList(mutableListOf<java.net.Socket>())
    init {
        thread(isDaemon = true) {
            while (!server.isClosed) {
                val socket = try { server.accept() } catch (_: java.io.IOException) { break }
                sockets.add(socket)
                thread(isDaemon = true) connection@{
                    socket.use {
                        try {
                            val reader = it.getInputStream().bufferedReader()
                            val path = reader.readLine()?.split(" ")?.getOrNull(1) ?: return@connection
                            paths.add(path)
                            while (!reader.readLine().isNullOrEmpty()) { }
                            if (path == "/slow") Thread.sleep(2000)
                            val body = "{\"message\":\"synthetic-fixture\"}"
                            val status = if (path == "/error") "400 Bad Request" else "200 OK"
                            it.getOutputStream().write(("HTTP/1.1 $status\r\nContent-Type: application/json\r\n" +
                                "Content-Length: ${body.toByteArray().size}\r\nConnection: close\r\n\r\n$body").toByteArray())
                        } catch (_: java.io.IOException) { /* Client cancellation closes its socket. */ }
                    }
                }
            }
        }
    }
    override fun close() {
        server.close()
        synchronized(sockets) { sockets.forEach { it.close() } }
    }
}
