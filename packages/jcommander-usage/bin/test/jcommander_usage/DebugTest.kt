package jcommander_usage

import com.beust.jcommander.*
import io.kotest.core.spec.style.FunSpec

class DebugTest : FunSpec({
    test("debug basic CLI") {
        @Parameters(commandNames = ["mycli"], commandDescription = "A simple CLI")
        class MyCli {
            @Parameter(names = ["-v", "--verbose"], description = "Enable verbose output")
            var verbose = false
            @Parameter(names = ["-c", "--config"], description = "Config file path")
            var config: String? = null
        }
        val jc = JCommander(MyCli())
        val spec = convertRoot(jc)
        println("name='${spec.name}'")
        println("about='${spec.about}'")
        println("flags: ${spec.flags.size}")
        for (f in spec.flags) {
            println("  flag long=${f.long} short=${f.short} help=${f.help}")
        }
    }
    
    test("debug main param") {
        class Cmd {
            @Parameter(description = "Input file")
            var file: String? = null
        }
        val jc = JCommander(Cmd())
        println("parameters count: ${jc.parameters.size}")
        for (pd in jc.parameters) {
            println("  param: name=${pd.parameterized.name} annotation=${pd.parameterAnnotation}")
            if (pd.parameterAnnotation != null) {
                println("    names=${pd.parameterAnnotation.names.contentToString()}")
            }
        }
        println("mainParameterValue: try...")
        try {
            println("  result: ${jc.mainParameterValue}")
        } catch (e: Throwable) {
            println("  ERROR: ${e.javaClass.simpleName}: ${e.message}")
        }
        val spec = convertRoot(jc)
        println("args: ${spec.args.size}")
        for (a in spec.args) {
            println("  arg: name=${a.name} required=${a.required}")
        }
    }
    
    test("debug boolean default") {
        class App {
            @Parameter(names = ["--color"], description = "Enable color")
            var color = true
        }
        val jc = JCommander(App())
        for (pd in jc.parameters) {
            println("  pd: ${pd.parameterized.name} default=${pd.default} type=${pd.parameterized.type}")
        }
        val spec = convertRoot(jc)
        for (f in spec.flags) {
            println("  flag: default=${f.default} defaultBool=${f.defaultBool}")
        }
    }
})
