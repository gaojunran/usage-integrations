rootProject.name = "usage-spec-monorepo"

include("usage-spec-kotlin")
include("picocli-usage")
include("clikt-usage")
include("jcommander-usage")

project(":usage-spec-kotlin").projectDir = file("packages/usage-spec-kotlin")
project(":picocli-usage").projectDir = file("packages/picocli-usage")
project(":clikt-usage").projectDir = file("packages/clikt-usage")
project(":jcommander-usage").projectDir = file("packages/jcommander-usage")

