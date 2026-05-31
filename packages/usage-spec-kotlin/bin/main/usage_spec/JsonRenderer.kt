package usage_spec

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

@Serializable
private data class JsonArg(
    val name: String,
    val help: String? = null,
    val required: Boolean? = null,
    val `var`: Boolean? = null,
    val hide: Boolean? = null,
    val default: String? = null,
    val defaults: List<String>? = null,
    val choices: List<String>? = null,
)

@Serializable
private data class JsonFlag(
    val name: String,
    val help: String? = null,
    val help_long: String? = null,
    val required: Boolean? = null,
    val hide: Boolean? = null,
    val global: Boolean? = null,
    val count: Boolean? = null,
    val `var`: Boolean? = null,
    val negate: String? = null,
    val deprecated: String? = null,
    val default: String? = null,
    val defaults: List<String>? = null,
    val env: String? = null,
    val arg: JsonArg? = null,
)

@Serializable
private data class JsonCommand(
    val name: String,
    val help: String? = null,
    val help_long: String? = null,
    val hide: Boolean? = null,
    val deprecated: String? = null,
    val aliases: List<String>? = null,
    val subcommand_required: Boolean? = null,
    val flags: List<JsonFlag>? = null,
    val args: List<JsonArg>? = null,
    val cmds: List<JsonCommand>? = null,
)

@Serializable
private data class JsonSpec(
    val name: String? = null,
    val bin: String? = null,
    val version: String? = null,
    val about: String? = null,
    val long_about: String? = null,
    val usage: String? = null,
    val flags: List<JsonFlag>? = null,
    val args: List<JsonArg>? = null,
    val cmds: List<JsonCommand>? = null,
)

private fun convertArg(arg: SpecArg): JsonArg {
    return JsonArg(
        name = arg.name,
        help = arg.help.takeIf { it.isNotEmpty() },
        required = if (!arg.required) false else null,
        `var` = if (arg.`var`) true else null,
        hide = if (arg.hide) true else null,
        default = arg.default.getOrNull(0),
        defaults = arg.default.takeIf { it.size > 1 },
        choices = arg.choices?.values,
    )
}

private fun convertFlag(flag: SpecFlag): JsonFlag {
    val nameParts = mutableListOf<String>()
    if (flag.short.isNotEmpty()) nameParts.add("-${flag.short}")
    if (flag.long.isNotEmpty()) nameParts.add("--${flag.long}")

    return JsonFlag(
        name = nameParts.joinToString(" "),
        help = flag.help.takeIf { it.isNotEmpty() },
        help_long = flag.helpLong.takeIf { it.isNotEmpty() },
        required = if (flag.required) true else null,
        hide = if (flag.hide) true else null,
        global = if (flag.global) true else null,
        count = if (flag.count) true else null,
        `var` = if (flag.`var`) true else null,
        negate = flag.negate.takeIf { it.isNotEmpty() },
        deprecated = flag.deprecated.takeIf { it.isNotEmpty() },
        default = flag.default.getOrNull(0)?.let { it } ?: flag.defaultBool?.let { it.toString() },
        defaults = flag.default.takeIf { it.size > 1 },
        env = flag.env.takeIf { it.isNotEmpty() },
        arg = flag.arg?.let(::convertArg),
    )
}

private fun convertCommand(cmd: SpecCommand): JsonCommand {
    return JsonCommand(
        name = cmd.name,
        help = cmd.help.takeIf { it.isNotEmpty() },
        help_long = cmd.helpLong.takeIf { it.isNotEmpty() },
        hide = if (cmd.hide) true else null,
        deprecated = cmd.deprecated.takeIf { it.isNotEmpty() },
        aliases = cmd.aliases.takeIf { it.isNotEmpty() },
        subcommand_required = if (cmd.subcommandRequired) true else null,
        flags = cmd.flags.map(::convertFlag).takeIf { it.isNotEmpty() },
        args = cmd.args.map(::convertArg).takeIf { it.isNotEmpty() },
        cmds = cmd.cmds.map(::convertCommand).takeIf { it.isNotEmpty() },
    )
}

fun renderJSON(spec: Spec): String {
    val jsonSpec = JsonSpec(
        name = spec.name.takeIf { it.isNotEmpty() },
        bin = spec.bin.takeIf { it.isNotEmpty() },
        version = spec.version.takeIf { it.isNotEmpty() },
        about = spec.about.takeIf { it.isNotEmpty() },
        long_about = spec.long.takeIf { it.isNotEmpty() },
        usage = spec.usage.takeIf { it.isNotEmpty() },
        flags = spec.flags.map(::convertFlag).takeIf { it.isNotEmpty() },
        args = spec.args.map(::convertArg).takeIf { it.isNotEmpty() },
        cmds = spec.cmds.map(::convertCommand).takeIf { it.isNotEmpty() },
    )

    return Json {
        prettyPrint = true
        encodeDefaults = false
    }.encodeToString(jsonSpec) + "\n"
}
