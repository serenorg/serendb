import Foundation

import PostgresClientKit

do {
    let env = ProcessInfo.processInfo.environment

    var configuration = PostgresClientKit.ConnectionConfiguration()
    let host = env["SERENDB_HOST"] ?? ""
    configuration.host = host
    configuration.port = 5432
    configuration.database = env["SERENDB_DATABASE"] ?? ""
    configuration.user = env["SERENDB_USER"] ?? ""

    // PostgresClientKit uses Kitura/BlueSSLService which doesn't support SNI
    // PostgresClientKit doesn't support setting connection options, so we use "Workaround D"
    // See https://serendb.com/sni
    let password = env["SERENDB_PASSWORD"] ?? ""
    let endpoint_id = host.split(separator: ".")[0]
    let workaroundD = "project=\(endpoint_id);\(password)"
    configuration.credential = .cleartextPassword(password: workaroundD)

    let connection = try PostgresClientKit.Connection(configuration: configuration)
    defer { connection.close() }

    let text = "SELECT 1;"
    let statement = try connection.prepareStatement(text: text)
    defer { statement.close() }

    let cursor = try statement.execute(parameterValues: [ ])
    defer { cursor.close() }

    for row in cursor {
        let columns = try row.get().columns
        print(columns[0])
    }
} catch {
    print(error)
}
