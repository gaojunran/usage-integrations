package clikt_usage

import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.core.Context
import com.github.ajalt.clikt.core.CoreCliktCommand
import com.github.ajalt.clikt.core.NoOpCliktCommand
import com.github.ajalt.clikt.completion.CompletionCandidates
import com.github.ajalt.clikt.parameters.arguments.Argument
import com.github.ajalt.clikt.parameters.options.Option
import com.github.ajalt.clikt.parameters.options.OptionWithValues
import com.github.ajalt.clikt.parameters.transform.HelpTransformContext
import usage_spec.Spec
import usage_spec.SpecArg
import usage_spec.SpecChoices
import usage_spec.SpecCommand
import usage_spec.SpecFlag

private val BUILTIN_FLAG_NAMES = setOf("help", "version")

private fun isBuiltinOption(opt: Option): Boolean {
    return opt.names.any { it.trimStart('-') in BUILTIN_FLAG_NAMES }
}

private fun isNoOpCommand(cmd: CoreCliktCommand): Boolean {
    return cmd is NoOpCliktCommand
}

private fun extractShortLong(names: Set<String>): Pair<String, String> {
    val short = names.find { it.startsWith("-") && !it.startsWith("--") }?.removePrefix("-") ?: ""
    val long = names.find { it.startsWith("--") }?.removePrefix("--") ?: ""
    return short to long
}

private fun createContext(cmd: CoreCliktCommand): Context? {
    return try {
        @Suppress("INVISIBLE_MEMBER", "INVISIBLE_REFERENCE")
        cmd.resetContext(null)
    } catch (_: Exception) {
        null
    }
}

private fun convertArg(arg: Argument, context: Context?): SpecArg {
    val required = arg.required
    val variadic = arg.nvalues < 0

    return SpecArg(
        name = arg.name,
        help = "",
        required = required,
        `var` = variadic,
        hide = false,
        default = emptyList(),
        choices = when (val candidates = arg.completionCandidates) {
            is CompletionCandidates.Fixed -> SpecChoices(values = candidates.candidates.toList())
            else -> null
        },
    )
}

private fun convertFlag(opt: Option, context: Context?): SpecFlag {
    val (short, long) = extractShortLong(opt.names)

    val help = context?.let { opt.optionHelp(it) } ?: ""

    val isBoolean = opt.nvalues == IntRange(0, 0)
    val negatedName = (opt.names + opt.secondaryNames).find { it.startsWith("--no-") }
    val positiveName = if (negatedName != null) {
        val derived = negatedName.replace("--no-", "--")
        if (derived in opt.names) derived else ""
    } else ""

    val required = opt.helpTags["required"] != null

    // Extract default values from helpTags
    val tagDefault = opt.helpTags["default"]
    val hasDefault = tagDefault != null

    var default: String? = null
    var defaultBool: Boolean? = null

    if (isBoolean) {
        // Boolean: true → render, false/null/empty → skip
        if (hasDefault && tagDefault == "true") {
            defaultBool = true
        }
    } else {
        // Non-boolean: non-empty string default → render
        if (hasDefault && tagDefault!!.isNotEmpty()) {
            default = tagDefault
        }
    }

    var flag = SpecFlag(
        short = short,
        long = long,
        help = help,
        helpLong = "",
        required = required,
        hide = opt.hidden,
        global = false,
        count = false,
        `var` = opt.nvalues.last > 1,
        negate = if (positiveName.isNotEmpty()) positiveName else "",
        deprecated = "",
        default = default?.let { listOf(it) } ?: emptyList(),
        defaultBool = defaultBool,
        env = if (opt is OptionWithValues<*, *, *>) opt.envvar ?: "" else "",
        arg = null,
    )

    if (!isBoolean) {
        val argRequired = opt.nvalues.first > 0
        val argVar = opt.nvalues.last > 1
        val argName = long.replace("-", "_").uppercase()
            .takeIf { it.isNotEmpty() }
            ?: short.uppercase()

        val arg = SpecArg(
            name = argName,
            help = "",
            required = argRequired,
            `var` = argVar,
            hide = false,
            default = emptyList(),
            choices = when (val candidates = opt.completionCandidates) {
                is CompletionCandidates.Fixed -> SpecChoices(values = candidates.candidates.toList())
                else -> null
            },
        )

        flag = flag.copy(arg = arg)
    }

    return flag
}

private fun convertCommand(cmd: CoreCliktCommand): SpecCommand {
    val context = createContext(cmd)

    val flags = mutableListOf<SpecFlag>()
    for (opt in cmd.registeredOptions()) {
        if (isBuiltinOption(opt)) continue
        flags.add(convertFlag(opt, context))
    }

    val args = mutableListOf<SpecArg>()
    for (arg in cmd.registeredArguments()) {
        args.add(convertArg(arg, context))
    }

    val cmds = mutableListOf<SpecCommand>()
    for (sub in cmd.registeredSubcommands()) {
        cmds.add(convertCommand(sub))
    }

    val subcommandRequired = cmds.isNotEmpty()
            && args.isEmpty()
            && isNoOpCommand(cmd)

    return SpecCommand(
        name = cmd.commandName,
        help = context?.let { cmd.help(it) } ?: "",
        helpLong = "",
        hide = cmd.hiddenFromHelp,
        deprecated = "",
        aliases = cmd.aliases().keys.toList(),
        subcommandRequired = subcommandRequired,
        flags = flags,
        args = args,
        cmds = cmds,
    )
}

fun convertRoot(cmd: CliktCommand, binName: String? = null): Spec {
    val name = binName ?: cmd.commandName
    val context = createContext(cmd)

    val flags = mutableListOf<SpecFlag>()
    for (opt in cmd.registeredOptions()) {
        if (isBuiltinOption(opt)) continue
        flags.add(convertFlag(opt, context))
    }

    val args = mutableListOf<SpecArg>()
    for (arg in cmd.registeredArguments()) {
        args.add(convertArg(arg, context))
    }

    val cmds = mutableListOf<SpecCommand>()
    for (sub in cmd.registeredSubcommands()) {
        cmds.add(convertCommand(sub))
    }

    return Spec(
        name = name,
        bin = name,
        version = "",
        about = context?.let { cmd.help(it) } ?: "",
        long = "",
        usage = "",
        flags = flags,
        args = args,
        cmds = cmds,
    )
}
