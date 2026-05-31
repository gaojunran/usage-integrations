package jcommander_usage

import com.beust.jcommander.*

@Parameters(commandNames = ["mycli"], commandDescription = "A simple CLI")
class MyCli {
    @Parameter(names = ["-v", "--verbose"], description = "Enable verbose output")
    var verbose = false

    @Parameter(names = ["-c", "--config"], description = "Config file path")
    var config: String? = null
}

fun main() {
    val jc = JCommander(MyCli())
    try {
        val output = generate(jc)
        println("SUCCESS")
        println(output)
    } catch (e: Throwable) {
        println("FAILED: ${e.javaClass.simpleName}: ${e.message}")
        e.printStackTrace()
    }
}
