using Npgsql;

var host = Environment.GetEnvironmentVariable("SERENDB_HOST");
var database = Environment.GetEnvironmentVariable("SERENDB_DATABASE");
var user = Environment.GetEnvironmentVariable("SERENDB_USER");
var password = Environment.GetEnvironmentVariable("SERENDB_PASSWORD");

var connString = $"Host={host};Username={user};Password={password};Database={database}";

await using var conn = new NpgsqlConnection(connString);
await conn.OpenAsync();

await using (var cmd = new NpgsqlCommand("SELECT 1", conn))
await using (var reader = await cmd.ExecuteReaderAsync())
{
    while (await reader.ReadAsync())
        Console.WriteLine(reader.GetInt32(0));
}
await conn.CloseAsync();
