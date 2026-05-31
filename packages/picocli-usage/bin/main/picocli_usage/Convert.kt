package picocli_usage

import picocli.CommandLine
import usage_spec.Spec
import usage_spec.SpecArg
import usage_spec.SpecChoices
import usage_spec.SpecCommand
import usage_spec.SpecFlag

private val BUILTIN_FLAG_NAMES = setOf("help", "version")

private fun isBuiltinOption(opt: CommandLine.Model.OptionSpec): Boolean {
    val name = opt.names().firstOrNull()?.trimStart('-') ?: return false
    return name in BUILTIN_FLAG_NAMES
}

private fun isRunnable(spec: CommandLine.Model.CommandSpec): Boolean {
    val userObject = spec.userObject() ?: return false
    return userObject is Runnable || userObject is java.util.concurrent.Callable<*>
}

private fun extractShortLong(names: Array<String>): Pair<String, String> {
    var short = ""
    var long = ""
    for (name in names) {
        when {
            name.startsWith("--") -> long = name.removePrefix("--")
            name.startsWith("-") -> short = name.removePrefix("-")
        }
    }
    return short to long
}

private fun parseArity(arity: CommandLine.Range): Pair<Boolean, Boolean> {
    val required = arity.min() > 0
    val variadic = arity.max() > 1
    return required to variadic
}

private fun convertArg(param: CommandLine.Model.PositionalParamSpec): SpecArg {
    val (required, variadic) = parseArity(param.arity())
    val label = param.paramLabel() ?: "ARG"

    val defaultValue = param.defaultValue()?.takeIf { it.isNotEmpty() }

    var result = SpecArg(
        name = label,
        help = param.description()?.firstOrNull() ?: "",
        required = required,
        `var` = variadic,
        hide = false,
        default = defaultValue?.let { listOf(it) } ?: emptyList(),
        choices = null,
    )

    val candidates = param.completionCandidates()
    if (candidates != null) {
        val values = candidates.toList()
        if (values.isNotEmpty()) {
            result = result.copy(choices = SpecChoices(values = values))
        }
    }

    return result
}

private fun convertFlag(opt: CommandLine.Model.OptionSpec, global: Boolean = false): SpecFlag {
    val (short, long) = extractShortLong(opt.names())

    // Boolean flag: arity min=0, max=0 OR type is Boolean
    val arity = opt.arity()
    val isBoolean = (arity.min() == 0 && arity.max() == 0)
        || opt.type() == Boolean::class.java
        || opt.type() == java.lang.Boolean::class.java

    var flag = SpecFlag(
        short = short,
        long = long,
        help = opt.description()?.firstOrNull() ?: "",
        helpLong = "",
        required = opt.required(),
        hide = opt.hidden(),
        global = global,
        count = false,
        `var` = arity.max() > 1,
        negate = if (opt.negatable() && long.isNotEmpty()) "--$long" else "",
        deprecated = "",
        default = emptyList(),
        defaultBool = null,
        env = "",
        arg = null,
    )

    if (!isBoolean) {
        val (argRequired, argVar) = parseArity(arity)
        val argName = long.replace("-", "_").uppercase()
            .takeIf { it.isNotEmpty() }
            ?: short.uppercase()

        var arg = SpecArg(
            name = argName,
            help = "",
            required = argRequired,
            `var` = argVar,
            hide = false,
            default = emptyList(),
            choices = null,
        )

        val candidates = opt.completionCandidates()
        if (candidates != null) {
            val values = candidates.toList()
            if (values.isNotEmpty()) {
                arg = arg.copy(choices = SpecChoices(values = values))
            }
        }

        flag = flag.copy(arg = arg)
    }

    // Default values
    val defaultValue = opt.defaultValue()
    if (defaultValue != null && defaultValue.isNotEmpty()) {
        flag = if (isBoolean) {
            when (defaultValue.lowercase()) {
                "true" -> flag.copy(defaultBool = true)
                "false" -> flag  // skip false default for boolean flags
                else -> flag.copy(default = listOf(defaultValue))
            }
        } else {
            flag.copy(default = listOf(defaultValue))
        }
    }

    return flag
}

private fun convertCommand(cmd: CommandLine): SpecCommand {
    val spec = cmd.commandSpec

    val flags = mutableListOf<SpecFlag>()
    for (opt in spec.options()) {
        if (isBuiltinOption(opt)) continue
        flags.add(convertFlag(opt))
    }

    val args = mutableListOf<SpecArg>()
    for (param in spec.positionalParameters()) {
        args.add(convertArg(param))
    }

    val cmds = mutableListOf<SpecCommand>()
    for ((_, sub) in spec.subcommands()) {
        cmds.add(convertCommand(sub))
    }

    val subcommandRequired = cmds.isNotEmpty()
            && args.isEmpty()
            && !isRunnable(spec)

    return SpecCommand(
        name = spec.name() ?: "",
        help = spec.usageMessage().description()?.firstOrNull() ?: "",
        helpLong = spec.usageMessage().description()?.drop(1)?.joinToString("\n") ?: "",
        hide = spec.usageMessage().hidden(),
        deprecated = "",
        aliases = spec.aliases().toList(),
        subcommandRequired = subcommandRequired,
        flags = flags,
        args = args,
        cmds = cmds,
    )
}

fun convertRoot(cmd: CommandLine, binName: String? = null): Spec {
    val spec = cmd.commandSpec
    val name = binName ?: spec.name() ?: ""

    val about = spec.usageMessage().description()?.firstOrNull() ?: ""
    val longAbout = spec.usageMessage().description()?.drop(1)?.joinToString("\n") ?: ""

    val flags = mutableListOf<SpecFlag>()
    for (opt in spec.options()) {
        if (isBuiltinOption(opt)) continue
        flags.add(convertFlag(opt))
    }

    val args = mutableListOf<SpecArg>()
    for (param in spec.positionalParameters()) {
        args.add(convertArg(param))
    }

    val cmds = mutableListOf<SpecCommand>()
    for ((_, sub) in spec.subcommands()) {
        cmds.add(convertCommand(sub))
    }

    return Spec(
        name = name,
        bin = name,
        version = spec.version()?.firstOrNull() ?: "",
        about = about,
        long = longAbout,
        usage = spec.usageMessage().customSynopsis()?.firstOrNull() ?: "",
        flags = flags,
        args = args,
        cmds = cmds,
    )
}
