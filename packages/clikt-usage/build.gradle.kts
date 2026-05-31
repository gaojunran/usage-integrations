plugins {
    kotlin("jvm")
    `maven-publish`
    signing
}

dependencies {
    implementation(project(":usage-spec-kotlin"))
    implementation("com.github.ajalt.clikt:clikt-jvm:5.0.3")

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

val artifactId = "clikt-usage"
val artifactDescription = "Generate usage-spec from Clikt CLI metadata"

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
