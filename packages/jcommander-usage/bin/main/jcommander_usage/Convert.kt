package jcommander_usage

import com.beust.jcommander.JCommander
import com.beust.jcommander.Parameter
import com.beust.jcommander.ParameterDescription
import com.beust.jcommander.Parameters
import com.beust.jcommander.WrappedParameter
import usage_spec.Spec
import usage_spec.SpecArg
import usage_spec.SpecCommand
import usage_spec.SpecFlag

private val BUILTIN_FLAG_NAMES = setOf("help", "version")

private fun isBuiltinOption(pd: ParameterDescription): Boolean {
    val wp = pd.parameter
    val names = wp.names()
    return names.any { it.trimStart('-') in BUILTIN_FLAG_NAMES }
}

private fun isBooleanType(pd: ParameterDescription): Boolean {
    val type = pd.parameterized.type
    return type == Boolean::class.javaPrimitiveType || type == Boolean::class.java
}

private fun isCollectionType(pd: ParameterDescription): Boolean {
    val type = pd.parameterized.type
    return List::class.java.isAssignableFrom(type) || Set::class.java.isAssignableFrom(type)
}

private fun extractShortLong(names: Array<String>): Pair<String, String> {
    val short = names.find { it.startsWith("-") && !it.startsWith("--") }?.removePrefix("-") ?: ""
    val long = names.find { it.startsWith("--") }?.removePrefix("--") ?: ""
    return short to long
}

private fun parseArity(wp: WrappedParameter, pd: ParameterDescription): Pair<Boolean, Boolean> {
    val arity = wp.arity()
    return when {
        arity == Parameter.DEFAULT_ARITY -> {
            if (isBooleanType(pd)) false to false else true to false
        }
        arity == 0 -> false to false
        arity < 0 -> false to false
        else -> (arity > 0) to (arity > 1)
    }
}

private fun convertArg(pd: ParameterDescription): SpecArg {
    val param = pd.parameterAnnotation
    val wp = pd.parameter
    val fieldName = pd.parameterized.name

    val required = param?.required == true
    val variadic = wp.variableArity() || isCollectionType(pd)

    val label = fieldName.uppercase()

    return SpecArg(
        name = label,
        help = pd.description ?: "",
        required = required,
        `var` = variadic,
        hide = wp.hidden(),
        default = emptyList(),
        choices = null,
    )
}

private fun convertFlag(pd: ParameterDescription): SpecFlag {
    val wp = pd.parameter
    val names = wp.names()
    val (short, long) = extractShortLong(names)

    val isBool = isBooleanType(pd)
    val required = wp.required()
    val hidden = wp.hidden()

    var flag = SpecFlag(
        short = short,
        long = long,
        help = pd.description ?: "",
        helpLong = "",
        required = required,
        hide = hidden,
        global = false,
        count = false,
        `var` = wp.variableArity() || (!isBool && wp.arity() > 1),
        negate = "",
        deprecated = "",
        default = emptyList(),
        defaultBool = null,
        env = "",
        arg = null,
    )

    if (!isBool) {
        val (argRequired, argVar) = parseArity(wp, pd)
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
            choices = null,
        )

        flag = flag.copy(arg = arg)
    }

    // Default values
    val defaultValue = pd.default
    if (defaultValue != null) {
        if (isBool) {
            if (defaultValue == true) {
                flag = flag.copy(defaultBool = true)
            }
        } else {
            val str = defaultValue.toString()
            if (str.isNotEmpty()) {
                flag = flag.copy(default = listOf(str))
            }
        }
    }

    return flag
}

private fun convertCommand(name: String, jc: JCommander): SpecCommand {
    val objects = jc.objects
    val mainObj = objects.firstOrNull()

    val paramsAnnotation = mainObj?.javaClass?.getAnnotation(Parameters::class.java)
    val help = paramsAnnotation?.commandDescription ?: ""
    val hidden = paramsAnnotation?.hidden ?: false

    val flags = mutableListOf<SpecFlag>()
    val args = mutableListOf<SpecArg>()

    // Main parameter - getMainParameterValue() throws NPE when there is no main parameter
    val mainPd = try { jc.mainParameterValue } catch (_: Throwable) { null }
    if (mainPd != null) {
        args.add(convertArg(mainPd))
    }

    for (pd in jc.parameters) {
        if (isBuiltinOption(pd)) continue
        val param = pd.parameterAnnotation
        if (param != null && param.names.isEmpty()) {
            if (mainPd == null) {
                args.add(convertArg(pd))
            }
        } else {
            flags.add(convertFlag(pd))
        }
    }

    val cmds = mutableListOf<SpecCommand>()
    for ((cmdName, subJc) in jc.commands) {
        cmds.add(convertCommand(cmdName, subJc))
    }

    val subcommandRequired = cmds.isNotEmpty() && args.isEmpty()

    return SpecCommand(
        name = name,
        help = help,
        helpLong = "",
        hide = hidden,
        deprecated = "",
        aliases = emptyList(),
        subcommandRequired = subcommandRequired,
        flags = flags,
        args = args,
        cmds = cmds,
    )
}

fun convertRoot(jc: JCommander, binName: String? = null): Spec {
    val name = binName ?: jc.programName ?: ""
    val objects = jc.objects
    val mainObj = objects.firstOrNull()

    val paramsAnnotation = mainObj?.javaClass?.getAnnotation(Parameters::class.java)
    val about = paramsAnnotation?.commandDescription ?: ""

    val flags = mutableListOf<SpecFlag>()
    val args = mutableListOf<SpecArg>()

    // Main parameter - getMainParameterValue() throws NPE when there is no main parameter
    val mainPd = try { jc.mainParameterValue } catch (_: Throwable) { null }
    if (mainPd != null) {
        args.add(convertArg(mainPd))
    }

    for (pd in jc.parameters) {
        if (isBuiltinOption(pd)) continue
        val param = pd.parameterAnnotation
        if (param != null && param.names.isEmpty()) {
            if (mainPd == null) {
                args.add(convertArg(pd))
            }
        } else {
            flags.add(convertFlag(pd))
        }
    }

    val cmds = mutableListOf<SpecCommand>()
    for ((cmdName, subJc) in jc.commands) {
        cmds.add(convertCommand(cmdName, subJc))
    }

    return Spec(
        name = name,
        bin = name,
        version = "",
        about = about,
        long = "",
        usage = "",
        flags = flags,
        args = args,
        cmds = cmds,
    )
}
