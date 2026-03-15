// Database helpers for Physics AI Dashboard

import { eq, desc } from "drizzle-orm";
import { getDb } from "./db";
import { 
  simulations, 
  predictions, 
  modelVersions, 
  ethicsLogs, 
  trainingJobs,
  type Simulation,
  type Prediction,
  type ModelVersion,
  type EthicsLog,
  type TrainingJob,
  type InsertSimulation,
  type InsertPrediction,
  type InsertModelVersion,
  type InsertEthicsLog,
  type InsertTrainingJob
} from "../drizzle/schema";

// Simulations
export async function createSimulation(data: InsertSimulation): Promise<Simulation | null> {
  const db = await getDb();
  if (!db) return null;
  
  const result = await db.insert(simulations).values(data);
  return result.length > 0 ? result[0] : null;
}

export async function getSimulation(id: number): Promise<Simulation | null> {
  const db = await getDb();
  if (!db) return null;
  
  const result = await db.select().from(simulations).where(eq(simulations.id, id)).limit(1);
  return result.length > 0 ? result[0] : null;
}

export async function getUserSimulations(userId: number): Promise<Simulation[]> {
  const db = await getDb();
  if (!db) return [];
  
  return await db.select().from(simulations).where(eq(simulations.userId, userId)).orderBy(desc(simulations.createdAt));
}

export async function updateSimulationStatus(id: number, status: string): Promise<void> {
  const db = await getDb();
  if (!db) return;
  
  await db.update(simulations).set({ status }).where(eq(simulations.id, id));
}

// Predictions
export async function cachePrediction(data: InsertPrediction): Promise<Prediction | null> {
  const db = await getDb();
  if (!db) return null;
  
  const result = await db.insert(predictions).values(data).onDuplicateKeyUpdate({
    set: {
      predictionMean: data.predictionMean,
      predictionStd: data.predictionStd
    }
  });
  
  return result.length > 0 ? result[0] : null;
}

export async function getPrediction(inputParams: any): Promise<Prediction | null> {
  const db = await getDb();
  if (!db) return null;
  
  const result = await db.select().from(predictions).where(eq(predictions.inputParams, inputParams)).limit(1);
  return result.length > 0 ? result[0] : null;
}

// Model Versions
export async function registerModelVersion(data: InsertModelVersion): Promise<ModelVersion | null> {
  const db = await getDb();
  if (!db) return null;
  
  const result = await db.insert(modelVersions).values(data);
  return result.length > 0 ? result[0] : null;
}

export async function getModelVersion(modelId: string, version: string): Promise<ModelVersion | null> {
  const db = await getDb();
  if (!db) return null;
  
  const result = await db.select().from(modelVersions)
    .where(eq(modelVersions.modelId, modelId) && eq(modelVersions.version, version))
    .limit(1);
  
  return result.length > 0 ? result[0] : null;
}

export async function getLatestModelVersion(modelId: string): Promise<ModelVersion | null> {
  const db = await getDb();
  if (!db) return null;
  
  const result = await db.select().from(modelVersions)
    .where(eq(modelVersions.modelId, modelId))
    .orderBy(desc(modelVersions.createdAt))
    .limit(1);
  
  return result.length > 0 ? result[0] : null;
}

export async function listModelVersions(modelId: string): Promise<ModelVersion[]> {
  const db = await getDb();
  if (!db) return [];
  
  return await db.select().from(modelVersions)
    .where(eq(modelVersions.modelId, modelId))
    .orderBy(desc(modelVersions.createdAt));
}

// Ethics Logs
export async function logEthicsValidation(data: InsertEthicsLog): Promise<EthicsLog | null> {
  const db = await getDb();
  if (!db) return null;
  
  const result = await db.insert(ethicsLogs).values(data);
  return result.length > 0 ? result[0] : null;
}

export async function getEthicsLogs(simulationId: number): Promise<EthicsLog[]> {
  const db = await getDb();
  if (!db) return [];
  
  return await db.select().from(ethicsLogs)
    .where(eq(ethicsLogs.simulationId, simulationId))
    .orderBy(desc(ethicsLogs.createdAt));
}

// Training Jobs
export async function createTrainingJob(data: InsertTrainingJob): Promise<TrainingJob | null> {
  const db = await getDb();
  if (!db) return null;
  
  const result = await db.insert(trainingJobs).values(data);
  return result.length > 0 ? result[0] : null;
}

export async function getTrainingJob(id: number): Promise<TrainingJob | null> {
  const db = await getDb();
  if (!db) return null;
  
  const result = await db.select().from(trainingJobs).where(eq(trainingJobs.id, id)).limit(1);
  return result.length > 0 ? result[0] : null;
}

export async function getUserTrainingJobs(userId: number): Promise<TrainingJob[]> {
  const db = await getDb();
  if (!db) return [];
  
  return await db.select().from(trainingJobs)
    .where(eq(trainingJobs.userId, userId))
    .orderBy(desc(trainingJobs.createdAt));
}

export async function updateTrainingJobProgress(id: number, progress: number, metrics?: any): Promise<void> {
  const db = await getDb();
  if (!db) return;
  
  await db.update(trainingJobs).set({ 
    progress,
    metrics: metrics ? JSON.stringify(metrics) : undefined
  }).where(eq(trainingJobs.id, id));
}

export async function completeTrainingJob(id: number, metrics: any): Promise<void> {
  const db = await getDb();
  if (!db) return;
  
  await db.update(trainingJobs).set({ 
    status: "completed",
    metrics: JSON.stringify(metrics),
    completedAt: new Date()
  }).where(eq(trainingJobs.id, id));
}
