#!/usr/bin/env node
// Score eval trials against assertions.json.
//   node score.mjs results/*.json
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const assertions = JSON.parse(
	readFileSync(join(here, 'assertions.json'), 'utf8'),
);

function transcriptFor(sessionId) {
	const found = execFileSync(
		'find',
		[`${process.env.HOME}/.claude/projects`, '-name', `${sessionId}.jsonl`],
		{ encoding: 'utf8' },
	)
		.trim()
		.split('\n')
		.filter(Boolean);
	if (!found.length) throw new Error(`no transcript for session ${sessionId}`);
	return found[0];
}

function toolStream(path) {
	const calls = [];
	for (const line of readFileSync(path, 'utf8').split('\n')) {
		if (!line.trim()) continue;
		let entry;
		try {
			entry = JSON.parse(line);
		} catch {
			continue;
		}
		if (entry.type !== 'assistant') continue;
		for (const part of entry.message?.content ?? []) {
			if (part.type !== 'tool_use') continue;
			calls.push({
				name: part.name,
				text:
					part.input?.command ??
					part.input?.file_path ??
					part.input?.pattern ??
					part.input?.query ??
					'',
			});
		}
	}
	return calls;
}

const trials = process.argv.slice(2).map((file) => {
	// A .jsonl argument is a transcript itself, which lets past runs be rescored.
	const raw = file.endsWith('.jsonl');
	const result = raw ? {} : JSON.parse(readFileSync(file, 'utf8'));
	const calls = toolStream(raw ? file : transcriptFor(result.session_id));
	const haystack = calls.map((c) => c.text).join('\n');
	let files = '',
		diff = '';
	try {
		files = readFileSync(file.replace(/\.jsonl?$/, '.files'), 'utf8');
	} catch {}
	try {
		diff = readFileSync(file.replace(/\.jsonl?$/, '.diff'), 'utf8');
	} catch {}
	let task = '';
	try {
		task = readFileSync(file.replace(/\.jsonl?$/, '.task'), 'utf8').trim();
	} catch {}
	return {
		label: file
			.split('/')
			.pop()
			.replace(/-\d{8}-\d{6}\.json$/, '')
			.replace(/\.jsonl$/, ''),
		seconds: result.duration_ms ? Math.round(result.duration_ms / 1000) : '-',
		calls: calls.length,
		error: result.is_error,
		verdicts: Object.fromEntries(
			assertions.map((a) => {
				if (a.tasks && !a.tasks.includes(task)) return [a.id, null];
				// An absent-pattern check against an uncaptured diff is vacuous, not a pass.
				if (a.on === 'diff' && !diff) return [a.id, null];
				const target =
					a.on === 'files' ? files
					: a.on === 'diff' ? diff
					: haystack;
				const hit = new RegExp(a.pattern, a.on === 'diff' ? 'm' : '').test(
					target,
				);
				return [a.id, a.expect === 'used' ? hit : !hit];
			}),
		),
	};
});

const width = Math.max(...assertions.map((a) => a.id.length), 12);
const head = trials.map((t) => t.label.padEnd(10)).join(' ');
console.log(`${'assertion'.padEnd(width)}  ${head}`);
for (const a of assertions) {
	const cells = trials
		.map((t) => {
			const v = t.verdicts[a.id];
			return (
				v === null ? 'n/a'
				: v ? 'pass'
				: 'FAIL').padEnd(10);
		})
		.join(' ');
	console.log(
		`${a.id.padEnd(width)}  ${cells}${a.disputed ? '   (disputed)' : ''}`,
	);
}
console.log(`${'-'.repeat(width)}  ${'-'.repeat(head.length)}`);
console.log(
	`${'tool calls'.padEnd(width)}  ${trials.map((t) => String(t.calls).padEnd(10)).join(' ')}`,
);
console.log(
	`${'seconds'.padEnd(width)}  ${trials.map((t) => String(t.seconds).padEnd(10)).join(' ')}`,
);
