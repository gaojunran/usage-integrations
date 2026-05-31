plugins {
    kotlin("jvm")
    `maven-publish`
    signing
}

dependencies {
    implementation(project(":usage-spec-kotlin"))
    implementation("org.jcommander:jcommander:1.83")

    testImplementation("io.kotest:kotest-runner-junit5:5.9.1")
    testImplementation("io.kotest:kotest-assertions-core:5.9.1")
}

tasks.test {
    useJUnitPlatform()
}

java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_21
    }
}

val sourcesJar by tasks.registering(Jar::class) {
    archiveClassifier.set("sources")
    from(sourceSets["main"].allSource)
}

val javadocJar by tasks.registering(Jar::class) {
    archiveClassifier.set("javadoc")
}

val artifactId = "jcommander-usage"
val artifactDescription = "Generate usage-spec from JCommander CLI metadata"

publishing {
    publications {
        create<MavenPublication>("maven") {
            artifact(tasks.jar)
            artifact(sourcesJar)
            artifact(javadocJar)
            this.artifactId = artifactId

            pom {
                name.set(artifactId)
                description.set(artifactDescription)
                url.set("https://github.com/gaojunran/usage-integrations")
                licenses {
                    license {
                        name.set("MIT")
                        url.set("https://opensource.org/licenses/MIT")
                    }
                }
                developers {
                    developer {
                        id.set("gaojunran")
                        name.set("Junran Gao")
                    }
                }
                scm {
                    connection.set("scm:git:git://github.com/gaojunran/usage-integrations.git")
                    developerConnection.set("scm:git:ssh://github.com:gaojunran/usage-integrations.git")
                    url.set("https://github.com/gaojunran/usage-integrations")
                }

                withXml {
                    val root = asNode()
                    val deps = root.appendNode("dependencies")

                    val dep = deps.appendNode("dependency")
                    dep.appendNode("groupId", "dev.usage-spec")
                    dep.appendNode("artifactId", "usage-spec-kotlin")
                    dep.appendNode("version", version)
                    dep.appendNode("scope", "runtime")

                    val jcDep = deps.appendNode("dependency")
                    jcDep.appendNode("groupId", "org.jcommander")
                    jcDep.appendNode("artifactId", "jcommander")
                    jcDep.appendNode("version", "1.83")
                    jcDep.appendNode("scope", "runtime")
                }
            }
        }
    }

    repositories {
        maven {
            name = "github"
            url = uri("https://maven.pkg.github.com/gaojunran/usage-integrations")
            credentials {
                username = findProperty("githubUsername")?.toString() ?: System.getenv("GITHUB_USERNAME")
                password = findProperty("githubToken")?.toString() ?: System.getenv("GITHUB_TOKEN")
            }
        }
    }
}
