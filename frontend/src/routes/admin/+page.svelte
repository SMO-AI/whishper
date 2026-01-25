<script>
	import { supabase } from '$lib/supabase';
	import { onMount } from 'svelte';
	import toast, { Toaster } from 'svelte-french-toast';
	import { goto } from '$app/navigation';
	import { fade, fly } from 'svelte/transition';

	let users = [];
	let logs = [];
	let transcriptionsData = [];
	let dailyStats = [];
	let loading = true;
	let dateFrom = '';
	let dateTo = '';
	let isAdmin = false;

	// Initial date range: current month
	const now = new Date();
	const firstDay = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
	const lastDay = new Date().toISOString().split('T')[0];

	dateFrom = firstDay;
	dateTo = lastDay;

	async function checkAuth() {
		const {
			data: { session }
		} = await supabase.auth.getSession();
		if (!session) {
			goto('/auth/login');
			return;
		}

		const { data: profile } = await supabase
			.from('whishper_profiles')
			.select('role')
			.eq('id', session.user.id)
			.single();

		if (
			profile?.role !== 'admin' &&
			profile?.role !== 'CEO' &&
			session.user.email !== 'modyazhenov@gmail.com'
		) {
			toast.error('Access denied');
			goto('/app');
			return;
		}
		isAdmin = true;
	}

	async function fetchData() {
		if (!isAdmin) return;
		loading = true;
		try {
			// 1. Fetch all profiles
			const { data: profiles, error: pErr } = await supabase
				.from('whishper_profiles')
				.select('*')
				.order('created_at', { ascending: false });
			if (pErr) throw pErr;

			// 2. Fetch usage logs within range
			let logsQuery = supabase.from('whishper_usage_logs').select('*');
			if (dateFrom) logsQuery = logsQuery.gte('created_at', `${dateFrom}T00:00:00`);
			if (dateTo) logsQuery = logsQuery.lte('created_at', `${dateTo}T23:59:59`);
			const { data: usageLogs, error: lErr } = await logsQuery;
			if (lErr) throw lErr;

			// 3. Fetch transcriptions for file metadata
			let transQuery = supabase.from('whishper_transcriptions').select('*');
			if (dateFrom) transQuery = transQuery.gte('created_at', `${dateFrom}T00:00:00`);
			if (dateTo) transQuery = transQuery.lte('created_at', `${dateTo}T23:59:59`);
			const { data: transcriptions, error: tErr } = await transQuery;
			if (tErr) throw tErr;

			logs = usageLogs;
			transcriptionsData = transcriptions;

			// 4. Group by day
			const grouped = {};
			transcriptions.forEach((t) => {
				const day = new Date(t.created_at).toISOString().split('T')[0];
				if (!grouped[day]) {
					grouped[day] = { date: day, count: 0, minutes: 0, size: 0, formats: {} };
				}
				grouped[day].count++;
				grouped[day].minutes += t.duration / 60;
				grouped[day].size += Number(t.file_size) || 0;
				const fmt = t.mimetype || 'unknown';
				grouped[day].formats[fmt] = (grouped[day].formats[fmt] || 0) + 1;
			});
			dailyStats = Object.values(grouped).sort((a, b) => a.date.localeCompare(b.date));

			// 5. Process Users
			users = profiles.map((p) => {
				const userLogs = logs.filter((l) => l.user_id === p.id);
				const userTrans = transcriptions.filter((t) => t.user_id === p.id);
				const totalSeconds = userLogs.reduce((acc, l) => acc + (Number(l.amount) || 0), 0);
				const totalCost = userLogs.reduce((acc, l) => acc + (Number(l.cost) || 0), 0);
				return { ...p, totalSeconds, totalCost, usageCount: userTrans.length };
			});
		} catch (e) {
			toast.error(e.message);
		} finally {
			loading = false;
		}
	}

	async function updateRole(user, role) {
		try {
			const { error } = await supabase.from('whishper_profiles').update({ role }).eq('id', user.id);
			if (error) throw error;
			toast.success(`User ${user.email} is now ${role}`);
			fetchData();
		} catch (e) {
			toast.error(e.message);
		}
	}

	async function toggleStatus(user) {
		const newStatus = user.status === 'active' ? 'paused' : 'active';
		try {
			const { error } = await supabase
				.from('whishper_profiles')
				.update({ status: newStatus })
				.eq('id', user.id);

			if (error) throw error;
			toast.success(`User ${user.email} is now ${newStatus}`);
			fetchData();
		} catch (e) {
			toast.error(e.message);
		}
	}

	onMount(async () => {
		await checkAuth();
		if (isAdmin) {
			fetchData();
			const interval = setInterval(fetchData, 30000);
			return () => clearInterval(interval);
		}
	});

	$: stats = {
		totalUsers: users.length,
		activeUsers: users.filter((u) => u.status === 'active').length,
		totalSpent: users.reduce((acc, u) => acc + u.totalCost, 0),
		totalHours: users.reduce((acc, u) => acc + u.totalSeconds, 0) / 3600
	};
</script>

<Toaster />

<div class="min-h-screen bg-base-100 p-4 md:p-8">
	<div class="max-w-7xl mx-auto">
		<!-- Header -->
		<header class="flex flex-col md:flex-row justify-between items-center gap-6 mb-12">
			<div>
				<h1
					class="text-4xl font-black bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent"
				>
					Admin Center
				</h1>
				<p class="opacity-60 font-medium">Monitoring and User Control</p>
			</div>

			<div
				class="flex flex-wrap items-center gap-4 bg-base-200 p-4 rounded-2xl shadow-inner border border-base-content/5"
			>
				<div class="form-control">
					<label class="label pb-1" for="date-from"
						><span class="label-text text-xs font-bold opacity-50 uppercase">From</span></label
					>
					<input
						id="date-from"
						type="date"
						bind:value={dateFrom}
						on:change={fetchData}
						class="input input-sm input-bordered rounded-lg bg-base-100"
					/>
				</div>
				<div class="form-control">
					<label class="label pb-1" for="date-to"
						><span class="label-text text-xs font-bold opacity-50 uppercase">To</span></label
					>
					<input
						id="date-to"
						type="date"
						bind:value={dateTo}
						on:change={fetchData}
						class="input input-sm input-bordered rounded-lg bg-base-100"
					/>
				</div>
				<div class="flex items-end h-full pt-6">
					<button on:click={fetchData} class="btn btn-sm btn-ghost btn-circle" title="Refresh">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-5 h-5"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /><path d="M12 7v5l3 3" /></svg
						>
					</button>
				</div>
			</div>
		</header>

		<!-- Stats Cards -->
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
			<div
				class="bg-gradient-to-br from-primary/10 to-primary/5 p-6 rounded-3xl border border-primary/10 shadow-xl shadow-primary/5"
				in:fly={{ y: 20, delay: 100 }}
			>
				<div class="text-primary opacity-60 text-xs font-black uppercase tracking-widest mb-1">
					Total Users
				</div>
				<div class="text-4xl font-black">{stats.totalUsers}</div>
				<div class="mt-2 text-xs opacity-50 font-bold">{stats.activeUsers} active now</div>
			</div>

			<div
				class="bg-gradient-to-br from-secondary/10 to-secondary/5 p-6 rounded-3xl border border-secondary/10 shadow-xl shadow-secondary/5"
				in:fly={{ y: 20, delay: 200 }}
			>
				<div class="text-secondary opacity-60 text-xs font-black uppercase tracking-widest mb-1">
					Total Spent
				</div>
				<div class="text-4xl font-black text-secondary">${stats.totalSpent.toFixed(4)}</div>
				<div class="mt-2 text-xs opacity-50 font-bold">Groq API Direct Cost</div>
			</div>

			<div
				class="bg-gradient-to-br from-accent/10 to-accent/5 p-6 rounded-3xl border border-accent/10 shadow-xl shadow-accent/5"
				in:fly={{ y: 20, delay: 300 }}
			>
				<div class="text-accent opacity-60 text-xs font-black uppercase tracking-widest mb-1">
					Transcribed
				</div>
				<div class="text-4xl font-black">
					{stats.totalHours.toFixed(2)} <span class="text-lg font-medium opacity-50">hrs</span>
				</div>
				<div class="mt-2 text-xs opacity-50 font-bold">Total audio processed</div>
			</div>

			<div
				class="bg-gradient-to-br from-base-content/10 to-base-content/5 p-6 rounded-3xl border border-base-content/10 shadow-xl"
				in:fly={{ y: 20, delay: 400 }}
			>
				<div class="opacity-60 text-xs font-black uppercase tracking-widest mb-1">Efficiency</div>
				<div class="text-4xl font-black">
					{(stats.totalSpent / (stats.totalHours || 1)).toFixed(3)}
					<span class="text-lg font-medium opacity-50">$/hr</span>
				</div>
				<div class="mt-2 text-xs opacity-50 font-bold">Avg model price</div>
			</div>
		</div>

		<!-- Daily Dashboard -->
		<div
			class="mb-12 bg-base-200/30 p-8 rounded-[2.5rem] border border-base-content/5 shadow-inner"
		>
			<div class="flex justify-between items-center mb-8">
				<h2 class="text-2xl font-black">Daily Activity</h2>
				<div
					class="flex gap-2 text-[10px] items-center opacity-50 font-black uppercase tracking-widest"
				>
					<span class="w-3 h-3 bg-primary rounded-full" /> Transcriptions
					<span class="ml-4 w-3 h-3 bg-secondary rounded-full" /> Minutes
				</div>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
				<div class="h-64 flex items-end gap-1 px-4">
					{#each dailyStats as day}
						<div class="flex-1 flex flex-col items-center group relative h-full justify-end">
							<div
								class="absolute bottom-full mb-2 bg-base-300 text-[10px] p-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity z-50 pointer-events-none whitespace-nowrap shadow-xl"
							>
								<div class="font-bold border-b border-base-content/10 mb-1">{day.date}</div>
								<div>Rows: {day.count}</div>
								<div>Mins: {day.minutes.toFixed(1)}</div>
								<div>Size: {(day.size / 1024 / 1024).toFixed(1)} MB</div>
								{#each Object.entries(day.formats) as [fmt, count]}
									<div class="opacity-60 text-[8px]">{fmt}: {count}</div>
								{/each}
							</div>
							<div
								class="w-full bg-primary/20 rounded-t-lg transition-all group-hover:bg-primary/40 relative"
								style="height: {(day.count / Math.max(...dailyStats.map((d) => d.count), 1)) *
									100}%"
							>
								<div
									class="absolute bottom-0 left-0 w-full bg-primary rounded-t-lg"
									style="height: 100%"
								/>
							</div>
							<div class="text-[8px] font-bold opacity-30 mt-2 truncate max-w-full">
								{day.date.split('-').slice(1).join('/')}
							</div>
						</div>
					{:else}
						<div class="w-full h-full flex items-center justify-center opacity-20 italic">
							No data for chart
						</div>
					{/each}
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div class="bg-base-100 p-4 rounded-2xl shadow-sm border border-base-content/5">
						<div class="text-[10px] font-black opacity-40 uppercase mb-2">Data Processed</div>
						<div class="text-2xl font-black">
							{(dailyStats.reduce((acc, d) => acc + d.size, 0) / 1024 / 1024 / 1024).toFixed(2)}
							<span class="text-xs opacity-50">GB</span>
						</div>
					</div>
					<div class="bg-base-100 p-4 rounded-2xl shadow-sm border border-base-content/5">
						<div class="text-[10px] font-black opacity-40 uppercase mb-2">Avg Session</div>
						<div class="text-2xl font-black">
							{(
								dailyStats.reduce((acc, d) => acc + d.minutes, 0) /
								(dailyStats.reduce((acc, d) => acc + d.count, 0) || 1)
							).toFixed(1)} <span class="text-xs opacity-50">min</span>
						</div>
					</div>
					<div
						class="bg-base-100 p-4 rounded-2xl shadow-sm border border-base-content/5 col-span-2"
					>
						<div class="text-[10px] font-black opacity-40 uppercase mb-4">File Format Stats</div>
						<div class="flex flex-wrap gap-2">
							{#each Object.entries(dailyStats.reduce((acc, d) => {
									Object.entries(d.formats).forEach(([f, c]) => (acc[f] = (acc[f] || 0) + c));
									return acc;
								}, {})) as [fmt, count]}
								<span class="badge badge-outline border-base-content/10 font-mono text-[10px]"
									>{fmt}: {count}</span
								>
							{/each}
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Main Content -->
		<div
			class="bg-base-200/50 backdrop-blur-xl rounded-[2.5rem] border border-base-content/5 shadow-2xl overflow-hidden"
		>
			{#if loading}
				<div class="py-32 flex flex-col items-center justify-center space-y-4">
					<span class="loading loading-ring loading-lg text-primary" />
					<span class="text-xs font-black uppercase tracking-[0.2em] opacity-40"
						>Synchronizing with Supabase</span
					>
				</div>
			{:else if users.length === 0}
				<div class="py-32 text-center opacity-40">
					<p class="text-xl font-bold italic">No users found for this selection.</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="table table-zebra w-full border-separate border-spacing-y-2 px-6">
						<thead>
							<tr class="text-xs font-black uppercase tracking-widest opacity-40 border-none">
								<th class="bg-transparent">User / Role</th>
								<th class="bg-transparent">Status</th>
								<th class="bg-transparent">Consumption</th>
								<th class="bg-transparent">Cost (USD)</th>
								<th class="bg-transparent text-right">Actions</th>
							</tr>
						</thead>
						<tbody>
							{#each users as user (user.id)}
								<tr
									class="bg-base-100 shadow-sm border-none group transition-all hover:scale-[1.01] hover:shadow-lg rounded-2xl"
								>
									<td class="rounded-l-2xl py-4">
										<div class="flex items-center gap-4">
											<div class="avatar placeholder">
												<div
													class="bg-gradient-to-tr {user.avatar_color ||
														'from-primary to-secondary'} text-white rounded-full w-12 shadow-lg rotate-3 group-hover:rotate-0 transition-transform"
												>
													<span class="text-lg font-black uppercase"
														>{user.email?.substring(0, 1)}</span
													>
												</div>
											</div>
											<div>
												<div class="font-black text-lg flex items-center gap-2">
													{user.email}
													<select
														class="select select-ghost select-xs text-[9px] font-black uppercase p-0 h-auto min-h-0 opacity-40 hover:opacity-100 transition-opacity"
														on:change={(e) => updateRole(user, e.target.value)}
														value={user.role || 'user'}
													>
														<option value="user">User</option>
														<option value="admin">Admin</option>
														<option value="CEO">CEO</option>
													</select>
												</div>
												<div class="text-[10px] font-mono opacity-30 uppercase">{user.id}</div>
											</div>
										</div>
									</td>
									<td>
										{#if user.status === 'active'}
											<span
												class="badge badge-success badge-sm font-black uppercase tracking-tighter shadow-sm shadow-success/20"
												>Active</span
											>
										{:else}
											<span
												class="badge badge-error badge-sm font-black uppercase tracking-tighter shadow-sm shadow-error/20"
												>Paused</span
											>
										{/if}
									</td>
									<td>
										<div class="flex flex-col">
											<span class="font-bold text-base"
												>{(user.totalSeconds / 60).toFixed(1)}
												<span class="text-xs opacity-50">min</span></span
											>
											<span class="text-[10px] opacity-40 font-bold uppercase"
												>{user.usageCount} transcriptions</span
											>
										</div>
									</td>
									<td>
										<div class="font-mono font-black text-primary text-lg">
											${user.totalCost.toFixed(4)}
										</div>
									</td>
									<td class="rounded-r-2xl text-right">
										<button
											on:click={() => toggleStatus(user)}
											class="btn btn-sm rounded-xl transition-all {user.status === 'active'
												? 'btn-outline btn-error hover:scale-105'
												: 'btn-success hover:scale-110 shadow-lg shadow-success/20'}"
										>
											{user.status === 'active' ? 'Pause account' : 'Activate Access'}
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
	</div>
</div>

<style>
	:global(.table tr:hover td) {
		background-color: transparent !important;
	}
	.table :where(thead, tfoot) :where(th, td) {
		background-color: transparent;
	}
</style>
