plugins {
    kotlin("jvm") version "2.3.21" apply false
    kotlin("plugin.serialization") version "2.3.21" apply false
    signing
}

allprojects {
    group = "dev.usage-spec"
    version = "1.1.0"

    repositories {
        mavenCentral()
        maven { url = uri("https://jitpack.io") }
    }
}
