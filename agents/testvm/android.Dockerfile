# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Flavio Visentin <flavio-activitytrack@infraconsulting.it>
# Android build image of the test VM runner (tag testvm): JDK 21 + SDK for compileSdk 37.
# Built by hand on the VM, not in CI:  mkdir /tmp/b && cp android.Dockerfile /tmp/b/Dockerfile && docker build -t activitytrack/android:37 /tmp/b
FROM eclipse-temurin:21-jdk
ENV DEBIAN_FRONTEND=noninteractive \
    ANDROID_HOME=/opt/android-sdk \
    ANDROID_SDK_ROOT=/opt/android-sdk
RUN apt-get update -qq \
 && apt-get install -y -qq --no-install-recommends curl unzip git ca-certificates > /dev/null \
 && rm -rf /var/lib/apt/lists/*
RUN mkdir -p "$ANDROID_HOME/cmdline-tools" "$ANDROID_HOME/licenses" \
 && curl -fsSL -o /tmp/cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip \
 && unzip -q /tmp/cmdline-tools.zip -d "$ANDROID_HOME/cmdline-tools" \
 && mv "$ANDROID_HOME/cmdline-tools/cmdline-tools" "$ANDROID_HOME/cmdline-tools/latest" \
 && rm /tmp/cmdline-tools.zip \
 && printf '\n24333f8a63b6825ea9c5514f83c2829b004d1fee\n8933bad161af4178b1185d1a37fbf41ea5269c55\nd56f5187479451eabf01fb78af6dfcb131a6481e\n' > "$ANDROID_HOME/licenses/android-sdk-license" \
 && "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" "platforms;android-37.0" "build-tools;36.0.0" > /dev/null \
 && chmod -R a+rX "$ANDROID_HOME"
ENV PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin"
