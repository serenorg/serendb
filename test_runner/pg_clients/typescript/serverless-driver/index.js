#! /usr/bin/env node

import ws from "ws";
import { serenDbConfig, Client } from "@serendb/serverless";

(async () => {
  serenDbConfig.webSocketConstructor = ws;

  const client = new Client({
    host: process.env.SERENDB_HOST,
    database: process.env.SERENDB_DATABASE,
    user: process.env.SERENDB_USER,
    password: process.env.SERENDB_PASSWORD,
  });
  client.connect();
  const result = await client.query({
    text: "select 1",
    rowMode: "array",
  });
  const rows = result.rows;
  await client.end();
  console.log(rows[0][0]);
})();
