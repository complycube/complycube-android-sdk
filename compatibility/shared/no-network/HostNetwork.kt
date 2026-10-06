package com.complycube.compat

object HostNetwork {
    fun run(baseUrl: String, report: (String) -> Unit) { report("Not selected") }
}
