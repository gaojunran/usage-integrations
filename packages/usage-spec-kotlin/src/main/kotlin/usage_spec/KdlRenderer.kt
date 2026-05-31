package usage_spec

import dev.kdl.KdlDocument
import dev.kdl.KdlNode
import dev.kdl.print.KdlPrinter

private fun buildChoicesNode(choices: SpecChoices): KdlNode {
    val builder = KdlNode.builder().name("choices")
    for (c in choices.values) {
        builder.argument(c)
    }
    return builder.build()
}

private fun buildArgNode(arg: SpecArg): KdlNode {
    val usage = buildString {
        if (arg.required) {
            append("<${arg.name}>")
        } else {
            append("[${arg.name}]")
        }
        if (arg.`var`) {
            append("\u2026")
        }
    }

    val builder = KdlNode.builder().name("arg").argument(usage)

    if (arg.help.isNotEmpty()) builder.property("help", arg.help)
    if (!arg.required) builder.property("required", false)
    if (arg.`var`) builder.property("var", true)
    if (arg.hide) builder.property("hide", true)
    if (arg.default.size == 1) builder.property("default", arg.default[0])

    val hasChildren = arg.choices != null || arg.default.size > 1
    if (hasChildren) {
        if (arg.default.size > 1) {
            val defaultBuilder = KdlNode.builder().name("default")
            for (d in arg.default) {
                defaultBuilder.argument(d)
            }
            builder.child(defaultBuilder.build())
        }
        if (arg.choices != null) {
            builder.child(buildChoicesNode(arg.choices))
        }
    }

    return builder.build()
}

private fun buildFlagArgNode(arg: SpecArg): KdlNode {
    val builder = KdlNode.builder().name("arg").argument("<${arg.name}>")
    if (arg.help.isNotEmpty()) builder.property("help", arg.help)
    if (arg.choices != null) {
        builder.child(buildChoicesNode(arg.choices))
    }
    return builder.build()
}

private fun buildFlagNode(flag: SpecFlag): KdlNode {
    val nameParts = mutableListOf<String>()
    if (flag.short.isNotEmpty()) nameParts.add("-${flag.short}")
    if (flag.long.isNotEmpty()) nameParts.add("--${flag.long}")
    val flagName = nameParts.joinToString(" ")

    val builder = KdlNode.builder().name("flag").argument(flagName)

    if (flag.help.isNotEmpty()) builder.property("help", flag.help)
    if (flag.required) builder.property("required", true)
    if (flag.`var`) builder.property("var", true)
    if (flag.hide) builder.property("hide", true)
    if (flag.global) builder.property("global", true)
    if (flag.count) builder.property("count", true)
    if (flag.negate.isNotEmpty()) builder.property("negate", flag.negate)
    if (flag.deprecated.isNotEmpty()) builder.property("deprecated", flag.deprecated)
    if (flag.default.size == 1) builder.property("default", flag.default[0])
    else if (flag.defaultBool != null) builder.property("default", flag.defaultBool)
    if (flag.env.isNotEmpty()) builder.property("env", flag.env)

    val hasChildren = flag.helpLong.isNotEmpty() || flag.arg != null || flag.default.size > 1
    if (hasChildren) {
        if (flag.helpLong.isNotEmpty()) {
            val longHelpBuilder = KdlNode.builder().name("long_help").argument(flag.helpLong)
            builder.child(longHelpBuilder.build())
        }
        if (flag.default.size > 1) {
            val defaultBuilder = KdlNode.builder().name("default")
            for (d in flag.default) {
                defaultBuilder.argument(d)
            }
            builder.child(defaultBuilder.build())
        }
        if (flag.arg != null) {
            builder.child(buildFlagArgNode(flag.arg))
        }
    }

    return builder.build()
}

private fun buildCommandNode(cmd: SpecCommand): KdlNode {
    val builder = KdlNode.builder().name("cmd").argument(cmd.name)

    if (cmd.hide) builder.property("hide", true)
    if (cmd.subcommandRequired) builder.property("subcommand_required", true)
    if (cmd.help.isNotEmpty()) builder.property("help", cmd.help)
    if (cmd.deprecated.isNotEmpty()) builder.property("deprecated", cmd.deprecated)

    val hasChildren = cmd.helpLong.isNotEmpty()
            || cmd.aliases.isNotEmpty()
            || cmd.flags.isNotEmpty()
            || cmd.args.isNotEmpty()
            || cmd.cmds.isNotEmpty()

    if (hasChildren) {
        if (cmd.aliases.isNotEmpty()) {
            val aliasBuilder = KdlNode.builder().name("alias")
            for (a in cmd.aliases) {
                aliasBuilder.argument(a)
            }
            builder.child(aliasBuilder.build())
        }
        if (cmd.helpLong.isNotEmpty()) {
            val longHelpBuilder = KdlNode.builder().name("long_help").argument(cmd.helpLong)
            builder.child(longHelpBuilder.build())
        }
        for (flag in cmd.flags) {
            builder.child(buildFlagNode(flag))
        }
        for (arg in cmd.args) {
            builder.child(buildArgNode(arg))
        }
        for (sub in cmd.cmds) {
            builder.child(buildCommandNode(sub))
        }
    }

    return builder.build()
}

fun renderKDL(spec: Spec): String {
    val docBuilder = KdlDocument.builder()

    if (spec.name.isNotEmpty()) {
        docBuilder.node(KdlNode.builder().name("name").argument(spec.name).build())
    }
    if (spec.bin.isNotEmpty()) {
        docBuilder.node(KdlNode.builder().name("bin").argument(spec.bin).build())
    }
    if (spec.version.isNotEmpty()) {
        docBuilder.node(KdlNode.builder().name("version").argument(spec.version).build())
    }
    if (spec.about.isNotEmpty()) {
        docBuilder.node(KdlNode.builder().name("about").argument(spec.about).build())
    }
    if (spec.long.isNotEmpty()) {
        docBuilder.node(KdlNode.builder().name("long_about").argument(spec.long).build())
    }
    if (spec.usage.isNotEmpty()) {
        docBuilder.node(KdlNode.builder().name("usage").argument(spec.usage).build())
    }

    for (flag in spec.flags) {
        docBuilder.node(buildFlagNode(flag))
    }
    for (arg in spec.args) {
        docBuilder.node(buildArgNode(arg))
    }
    for (cmd in spec.cmds) {
        docBuilder.node(buildCommandNode(cmd))
    }

    val writer = java.io.StringWriter()
    KdlPrinter().print(docBuilder.build(), writer)
    return writer.toString()
}
