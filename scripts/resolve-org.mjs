#!/usr/bin/env node
import { readFileSync } from 'fs';
const cfg = JSON.parse(readFileSync('manifest-config.json', 'utf8'));
console.log(cfg.override_org || cfg.source_org || 'embeddedos-org');
