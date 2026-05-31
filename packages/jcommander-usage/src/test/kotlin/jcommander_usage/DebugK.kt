package jcommander_usage

import com.beust.jcommander.*

fun main() {
    class App {
        @Parameter(names = ["--color"], description = "Enable color")
        var color = true
    }
    val jc = JCommander(App())
    val spec = convertRoot(jc)
    println("flags size: ${spec.flags.size}")
    for (f in spec.flags) {
        println("  long=${f.long} default=${f.default} defaultBool=${f.defaultBool}")
    }
}
