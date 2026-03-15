import { int, mysqlEnum, mysqlTable, text, timestamp, varchar, boolean, json, float } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

// Physics AI Dashboard Tables
export const simulations = mysqlTable("simulations", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("user_id").references(() => users.id),
  name: varchar("name", { length: 255 }).notNull(),
  description: text("description"),
  parameters: json("parameters").notNull(),
  status: varchar("status", { length: 50 }).default("pending").notNull(),
  resultUrl: text("result_url"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Simulation = typeof simulations.$inferSelect;
export type InsertSimulation = typeof simulations.$inferInsert;

export const predictions = mysqlTable("predictions", {
  id: int("id").autoincrement().primaryKey(),
  inputParams: json("input_params").notNull(),
  predictionMean: json("prediction_mean").notNull(),
  predictionStd: json("prediction_std"),
  modelVersion: varchar("model_version", { length: 50 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type Prediction = typeof predictions.$inferSelect;
export type InsertPrediction = typeof predictions.$inferInsert;

export const modelVersions = mysqlTable("model_versions", {
  id: int("id").autoincrement().primaryKey(),
  modelId: varchar("model_id", { length: 255 }).notNull(),
  version: varchar("version", { length: 50 }).notNull(),
  modelPath: text("model_path").notNull(),
  onnxPath: text("onnx_path"),
  config: json("config"),
  metrics: json("metrics"),
  trainingDataHash: varchar("training_data_hash", { length: 255 }),
  modelHash: varchar("model_hash", { length: 255 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type ModelVersion = typeof modelVersions.$inferSelect;
export type InsertModelVersion = typeof modelVersions.$inferInsert;

export const ethicsLogs = mysqlTable("ethics_logs", {
  id: int("id").autoincrement().primaryKey(),
  simulationId: int("simulation_id").references(() => simulations.id),
  violations: json("violations"),
  ethicsScore: int("ethics_score"),
  isEthical: boolean("is_ethical").default(false),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type EthicsLog = typeof ethicsLogs.$inferSelect;
export type InsertEthicsLog = typeof ethicsLogs.$inferInsert;

export const trainingJobs = mysqlTable("training_jobs", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("user_id").references(() => users.id),
  modelId: varchar("model_id", { length: 255 }).notNull(),
  datasetPath: text("dataset_path"),
  config: text("config"),
  status: varchar("status", { length: 50 }).default("pending").notNull(),
  progress: int("progress").default(0),
  metrics: text("metrics"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  completedAt: timestamp("completedAt"),
});

export type TrainingJob = typeof trainingJobs.$inferSelect;
export type InsertTrainingJob = typeof trainingJobs.$inferInsert;