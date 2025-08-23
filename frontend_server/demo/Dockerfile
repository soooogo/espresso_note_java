FROM openjdk:17-jdk-slim

WORKDIR /app

# Maven Wrapperとpom.xmlをコピー
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

# Maven Wrapperに実行権限を付与
RUN chmod +x mvnw

# 依存関係をダウンロード
RUN ./mvnw dependency:go-offline -B

# ソースコードをコピー
COPY src src

# アプリケーションをビルド
RUN ./mvnw package -DskipTests

# ポート8080を公開
EXPOSE 8080

# アプリケーションを起動
CMD ["java", "-jar", "target/demo-0.0.1-SNAPSHOT.jar"]
