package usage_spec

data class SpecChoices(
    val values: List<String>,
)

data class SpecArg(
    val name: String,
    val help: String,
    val required: Boolean,
    val `var`: Boolean,
    val hide: Boolean,
    val default: List<String>,
    val choices: SpecChoices?,
)

data class SpecFlag(
    val short: String,
    val long: String,
    val help: String,
    val helpLong: String,
    val required: Boolean,
    val hide: Boolean,
    val global: Boolean,
    val count: Boolean,
    val `var`: Boolean,
    val negate: String,
    val deprecated: String,
    val default: List<String>,
    val defaultBool: Boolean?,
    val env: String,
    val arg: SpecArg?,
)

data class SpecCommand(
    val name: String,
    val help: String,
    val helpLong: String,
    val hide: Boolean,
    val deprecated: String,
    val aliases: List<String>,
    val subcommandRequired: Boolean,
    val flags: List<SpecFlag>,
    val args: List<SpecArg>,
    val cmds: List<SpecCommand>,
)

data class Spec(
    val name: String,
    val bin: String,
    val version: String,
    val about: String,
    val long: String,
    val usage: String,
    val flags: List<SpecFlag>,
    val args: List<SpecArg>,
    val cmds: List<SpecCommand>,
)
