package usagespec

func Generate(spec Spec, format string, comment string) string {
	var output string
	if format == "json" {
		output = RenderJSON(spec)
	} else {
		output = RenderKDL(spec)
	}
	if comment != "" {
		return "// " + comment + "\n" + output
	}
	return output
}
