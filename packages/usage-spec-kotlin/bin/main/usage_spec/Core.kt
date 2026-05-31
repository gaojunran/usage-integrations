package usage_spec

import dev.kdl.parse.KdlParser

fun generate(
    spec: Spec,
    format: String = "kdl",
    comment: String? = null,
): String {
    val output = if (format == "json") renderJSON(spec) else renderKDL(spec)
    return if (comment != null) "// $comment\n$output" else output
}

fun validateKDL(kdl: String) {
    KdlParser.v2().parse(kdl)
}
