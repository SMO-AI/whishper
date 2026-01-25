<script>
	import { supabase } from '$lib/supabase';
	import { onMount } from 'svelte';
	import toast, { Toaster } from 'svelte-french-toast';
	import { goto } from '$app/navigation';
	import { fade, fly, scale } from 'svelte/transition';

	let users = [];
	let logs = [];
	let transcriptionsData = [];
	let dailyStats = [];
	let loading = true;
	let dateFrom = '';
	let dateTo = '';
	let isAdmin = false;
	let activeTab = 'users'; // 'users' or 'logs'

	// User Modal State
	let selectedUser = null;
	let userActivity = [];
	let loadingActivity = false;

	// Global Feed State
	let globalFeed = [];

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

			// 6. Global Feed Processing
			globalFeed = transcriptions
				.map((t) => {
					const profile = profiles.find((p) => p.id === t.user_id);
					const logEntry = usageLogs.find((l) => l.transcription_id === t.id);
					return {
						...t,
						user_email: profile?.email || 'Unknown',
						user_avatar: profile?.avatar_color,
						cost: logEntry?.cost || 0
					};
				})
				.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

			if (selectedUser) {
				selectedUser = users.find((u) => u.id === selectedUser.id) || null;
			}
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

	async function deleteUser(user) {
		if (
			!confirm(
				`Are you sure you want to delete user ${user.email}? This will remove all their data permanently.`
			)
		)
			return;
		try {
			const { error } = await supabase.from('whishper_profiles').delete().eq('id', user.id);
			if (error) throw error;
			toast.success('User deleted successfully');
			selectedUser = null;
			fetchData();
		} catch (e) {
			toast.error(e.message);
		}
	}

	async function openUserDetails(user) {
		selectedUser = user;
		loadingActivity = true;
		try {
			const { data: activity, error } = await supabase
				.from('whishper_transcriptions')
				.select('*, whishper_usage_logs(*)')
				.eq('user_id', user.id)
				.order('created_at', { ascending: false })
				.limit(10);
			if (error) throw error;
			userActivity = activity;
		} catch (e) {
			console.error(e);
		} finally {
			loadingActivity = false;
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
		totalSpent: users.reduce((acc, u) => acc + (u.totalCost || 0), 0),
		totalHours: users.reduce((acc, u) => acc + (u.totalSeconds || 0), 0) / 3600
	};

	function formatDate(dateStr) {
		if (!dateStr) return 'N/A';
		const date = new Date(dateStr);
		return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
	}

	function formatDateTime(dateStr) {
		if (!dateStr) return 'N/A';
		const date = new Date(dateStr);
		return date.toLocaleString('ru-RU', {
			day: '2-digit',
			month: '2-digit',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		});
	}

	function getTimeSince(dateStr) {
		if (!dateStr) return '';
		const seconds = Math.floor((new Date() - new Date(dateStr)) / 1000);
		let interval = seconds / 31536000;
		if (interval > 1) return Math.floor(interval) + ' years ago';
		interval = seconds / 2592000;
		if (interval > 1) return Math.floor(interval) + ' months ago';
		interval = seconds / 86400;
		if (interval > 1) return Math.floor(interval) + ' days ago';
		interval = seconds / 3600;
		if (interval > 1) return Math.floor(interval) + ' hours ago';
		interval = seconds / 60;
		if (interval > 1) return Math.floor(interval) + ' minutes ago';
		return Math.floor(seconds) + ' seconds ago';
	}
</script>

<Toaster />

<div class="min-h-screen bg-base-100 p-4 md:p-8">
	<div class="max-w-7xl mx-auto">
		<!-- Header -->
		<header class="flex flex-col md:flex-row justify-between items-center gap-6 mb-12">
			<div on:click={() => goto('/app')} class="cursor-pointer group">
				<h1
					class="text-4xl font-black bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent group-hover:from-secondary group-hover:to-primary transition-all duration-500"
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
					<button
						on:click={fetchData}
						class="btn btn-sm btn-ghost btn-circle {loading ? 'animate-spin' : ''}"
						title="Refresh"
					>
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
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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

		<!-- Tab Switcher -->
		<div class="flex justify-center mb-12">
			<div
				class="bg-base-200 p-1.5 rounded-2xl flex gap-1 shadow-inner border border-base-content/5"
			>
				<button
					on:click={() => (activeTab = 'users')}
					class="px-8 py-3 rounded-xl text-sm font-black uppercase tracking-widest transition-all {activeTab ===
					'users'
						? 'bg-primary text-white shadow-lg'
						: 'hover:bg-base-300 opacity-40'}"
				>
					Users Control
				</button>
				<button
					on:click={() => (activeTab = 'logs')}
					class="px-8 py-3 rounded-xl text-sm font-black uppercase tracking-widest transition-all {activeTab ===
					'logs'
						? 'bg-secondary text-white shadow-lg'
						: 'hover:bg-base-300 opacity-40'}"
				>
					Live Activity Log
				</button>
			</div>
		</div>

		<!-- Daily Dashboard (Only on Users Tab) -->
		{#if activeTab === 'users'}
			<div
				class="mb-12 bg-base-200/30 p-8 rounded-[2.5rem] border border-base-content/5 shadow-inner"
				transition:fade
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
		{/if}

		<!-- Main Content Area -->
		<div
			class="bg-base-200/50 backdrop-blur-xl rounded-[2.5rem] border border-base-content/5 shadow-2xl overflow-hidden min-h-[400px]"
		>
			{#if loading && users.length === 0}
				<div class="py-32 flex flex-col items-center justify-center space-y-4">
					<span class="loading loading-ring loading-lg text-primary" />
					<span class="text-xs font-black uppercase tracking-[0.2em] opacity-40"
						>Synchronizing with Supabase</span
					>
				</div>
			{:else if activeTab === 'users'}
				<div class="overflow-x-auto" transition:fade>
					<table class="table table-zebra w-full border-separate border-spacing-y-2 px-6">
						<thead>
							<tr class="text-xs font-black uppercase tracking-widest opacity-40 border-none">
								<th class="bg-transparent">User / Role</th>
								<th class="bg-transparent">Registered</th>
								<th class="bg-transparent">Status</th>
								<th class="bg-transparent">Consumption</th>
								<th class="bg-transparent">Cost (USD)</th>
								<th class="bg-transparent text-right">Actions</th>
							</tr>
						</thead>
						<tbody>
							{#each users as user (user.id)}
								<tr
									on:click={() => openUserDetails(user)}
									class="bg-base-100 shadow-sm border-none group transition-all hover:scale-[1.01] hover:shadow-lg rounded-2xl cursor-pointer"
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
													<span
														class="text-[9px] font-black uppercase px-2 py-0.5 bg-base-200 rounded opacity-40 group-hover:opacity-100 transition-opacity"
													>
														{user.role || 'user'}
													</span>
												</div>
												<div class="text-[10px] font-mono opacity-30 uppercase">{user.id}</div>
											</div>
										</div>
									</td>
									<td>
										<div class="flex flex-col">
											<span class="font-bold text-sm">{formatDate(user.created_at)}</span>
											<span class="text-[9px] opacity-30 uppercase font-black"
												>{getTimeSince(user.created_at)}</span
											>
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
											${(user.totalCost || 0).toFixed(4)}
										</div>
									</td>
									<td class="rounded-r-2xl text-right">
										<div class="flex justify-end gap-2">
											<button
												on:click|stopPropagation={() => toggleStatus(user)}
												class="btn btn-xs rounded-lg transition-all {user.status === 'active'
													? 'btn-outline btn-error'
													: 'btn-success shadow-lg shadow-success/20'}"
											>
												{user.status === 'active' ? 'Pause' : 'Activate'}
											</button>
											<button class="btn btn-xs btn-ghost btn-circle">
												<svg
													xmlns="http://www.w3.org/2000/svg"
													class="w-4 h-4"
													viewBox="0 0 24 24"
													fill="none"
													stroke="currentColor"
													stroke-width="2"><path d="M9 5l7 7-7 7" /></svg
												>
											</button>
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{:else if activeTab === 'logs'}
				<!-- Live Global Feed -->
				<div class="p-8" transition:fade>
					<div class="flex justify-between items-center mb-10">
						<div>
							<h2 class="text-2xl font-black italic">Network Pulse</h2>
							<p class="text-xs opacity-40 font-bold uppercase tracking-widest">
								Global Activity Stream
							</p>
						</div>
						<div class="flex items-center gap-2">
							<span class="relative flex h-2 w-2">
								<span
									class="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary opacity-75"
								/>
								<span class="relative inline-flex rounded-full h-2 w-2 bg-secondary" />
							</span>
							<span class="text-[10px] font-black uppercase opacity-60">Live Monitoring</span>
						</div>
					</div>

					{#if globalFeed.length === 0}
						<div class="py-20 text-center italic opacity-30">
							No transactions recorded in this period.
						</div>
					{:else}
						<div class="space-y-4">
							{#each globalFeed as log (log.id)}
								<div
									class="bg-base-100 p-6 rounded-3xl border border-base-content/5 flex items-center justify-between group hover:border-primary/20 transition-all hover:shadow-xl hover:shadow-primary/5 hover:-translate-y-0.5"
									in:fly={{ y: 20 }}
								>
									<div class="flex items-center gap-6">
										<div class="avatar placeholder">
											<div
												class="bg-gradient-to-tr {log.user_avatar ||
													'from-primary to-secondary'} text-white rounded-2xl w-14 h-14 shadow-lg group-hover:rotate-6 transition-transform"
											>
												<span class="text-xl font-black uppercase"
													>{log.user_email?.substring(0, 1)}</span
												>
											</div>
										</div>
										<div>
											<div class="flex items-center gap-3">
												<span class="font-black text-primary">{log.user_email}</span>
												<span class="badge badge-ghost badge-xs opacity-50 font-mono"
													>{log.id.split('-')[0]}</span
												>
											</div>
											<div class="flex items-center gap-2 mt-1">
												<span class="text-sm font-bold truncate max-w-[300px]"
													>{log.filename || log.name || log.mimetype || 'Unnamed Task'}</span
												>
												<span
													class="text-[10px] bg-secondary/10 text-secondary px-2 py-0.5 rounded font-black uppercase"
													>{(log.duration / 60).toFixed(1)} min</span
												>
											</div>
											<p class="text-[9px] font-black opacity-30 uppercase mt-2 tracking-tighter">
												{formatDateTime(log.created_at)} • {getTimeSince(log.created_at)}
											</p>
										</div>
									</div>

									<div class="text-right">
										<div class="text-2xl font-black font-mono text-secondary">
											${(log.cost || 0).toFixed(4)}
										</div>
										<div class="text-[9px] font-black uppercase opacity-40">
											Groq API Direct Charge
										</div>
										<div class="mt-2 flex justify-end gap-1">
											{#if log.mimetype?.includes('audio')}
												<span class="badge badge-outline text-[8px] font-black">AUDIO</span>
											{:else if log.mimetype?.includes('video')}
												<span class="badge badge-outline text-[8px] font-black">VIDEO</span>
											{/if}
											<span class="badge badge-primary badge-outline text-[8px] font-black"
												>TRANSCRIPTION</span
											>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>

<!-- User Details Modal (Keep existing) -->
{#if selectedUser}
	<div
		class="fixed inset-0 bg-base-300/80 backdrop-blur-md z-[100] flex items-center justify-center p-4"
		transition:fade={{ duration: 200 }}
		on:click|self={() => (selectedUser = null)}
	>
		<div
			class="bg-base-100 w-full max-w-4xl max-h-[90vh] rounded-[2.5rem] shadow-2xl border border-base-content/5 overflow-hidden flex flex-col"
			transition:scale={{ start: 0.9, duration: 300, opacity: 0 }}
		>
			<!-- Modal Header -->
			<div
				class="p-8 bg-gradient-to-br from-base-200 to-base-100 flex justify-between items-start border-b border-base-content/5"
			>
				<div class="flex items-center gap-6">
					<div class="avatar placeholder">
						<div
							class="bg-gradient-to-tr {selectedUser.avatar_color ||
								'from-primary to-secondary'} text-white rounded-3xl w-24 h-24 shadow-2xl rotate-3"
						>
							<span class="text-4xl font-black uppercase"
								>{selectedUser.email?.substring(0, 1)}</span
							>
						</div>
					</div>
					<div>
						<div class="flex items-center gap-3 mb-1">
							<h2 class="text-3xl font-black">{selectedUser.email}</h2>
							{#if selectedUser.status === 'active'}
								<span class="badge badge-success badge-lg font-black uppercase text-[10px]"
									>Active</span
								>
							{:else}
								<span class="badge badge-error badge-lg font-black uppercase text-[10px]"
									>Paused</span
								>
							{/if}
						</div>
						<p class="opacity-40 font-mono text-xs uppercase tracking-widest">{selectedUser.id}</p>
						<div class="mt-4 flex gap-4">
							<div class="flex flex-col">
								<span class="text-[9px] font-black opacity-30 uppercase">Role</span>
								<select
									class="select select-ghost select-xs text-xs font-black uppercase p-0 h-auto min-h-0 text-primary"
									on:change={(e) => updateRole(selectedUser, e.target.value)}
									value={selectedUser.role || 'user'}
								>
									<option value="user">User</option>
									<option value="admin">Admin</option>
									<option value="CEO">CEO</option>
								</select>
							</div>
							<div class="flex flex-col border-l border-base-content/10 pl-4">
								<span class="text-[9px] font-black opacity-30 uppercase">Member Since</span>
								<span class="text-xs font-black">{formatDate(selectedUser.created_at)}</span>
							</div>
						</div>
					</div>
				</div>
				<button on:click={() => (selectedUser = null)} class="btn btn-ghost btn-circle">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="w-6 h-6"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/></svg
					>
				</button>
			</div>

			<div class="flex-1 overflow-y-auto p-8">
				<div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
					<div class="bg-base-200/50 p-6 rounded-3xl border border-base-content/5">
						<span class="text-[10px] font-black opacity-30 uppercase block mb-2"
							>Total Consumption</span
						>
						<div class="text-3xl font-black">
							{(selectedUser.totalSeconds / 3600).toFixed(2)}
							<span class="text-sm opacity-40">hrs</span>
						</div>
						<div class="text-xs opacity-50 mt-1 font-bold">
							{selectedUser.usageCount} total actions
						</div>
					</div>
					<div class="bg-base-200/50 p-6 rounded-3xl border border-base-content/5">
						<span class="text-[10px] font-black opacity-30 uppercase block mb-2"
							>Revenue Influence</span
						>
						<div class="text-3xl font-black text-secondary">
							${(selectedUser.totalCost || 0).toFixed(3)}
						</div>
						<div class="text-xs opacity-50 mt-1 font-bold">Groq platform cost</div>
					</div>
					<div class="bg-base-200/50 p-6 rounded-3xl border border-base-content/5">
						<span class="text-[10px] font-black opacity-30 uppercase block mb-2">Avg Session</span>
						<div class="text-3xl font-black">
							{(selectedUser.totalSeconds / 60 / (selectedUser.usageCount || 1)).toFixed(1)}
							<span class="text-sm opacity-40">min</span>
						</div>
						<div class="text-xs opacity-50 mt-1 font-bold">Efficiency metric</div>
					</div>
				</div>

				<!-- Activity Section -->
				<div class="mb-8">
					<div class="flex justify-between items-center mb-6">
						<h3 class="text-xl font-black italic">Activity Logic</h3>
						<span class="text-[10px] font-black opacity-30 uppercase">Last 10 sessions</span>
					</div>

					{#if loadingActivity}
						<div class="flex justify-center py-12">
							<span class="loading loading-spinner text-primary" />
						</div>
					{:else if userActivity.length === 0}
						<div class="bg-base-200 rounded-3xl py-12 text-center italic opacity-30">
							No recent activity detected.
						</div>
					{:else}
						<div class="space-y-3">
							{#each userActivity as act}
								<div
									class="bg-base-200/40 p-4 rounded-2xl flex justify-between items-center hover:bg-base-200 transition-colors"
								>
									<div class="flex items-center gap-4">
										<div
											class="w-10 h-10 rounded-xl bg-base-100 flex items-center justify-center text-primary shadow-sm"
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												class="w-5 h-5"
												viewBox="0 0 24 24"
												fill="none"
												stroke="currentColor"
												stroke-width="2"
												><path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" /></svg
											>
										</div>
										<div>
											<div class="font-bold text-sm truncate max-w-[200px]">
												{act.filename || act.name || act.mimetype || 'Transcription'}
											</div>
											<div class="text-[10px] opacity-40 uppercase font-black">
												{getTimeSince(act.created_at)}
											</div>
										</div>
									</div>
									<div class="text-right">
										<div class="font-mono text-sm font-black">
											{(act.duration / 60).toFixed(1)}m
										</div>
										<div class="text-[10px] opacity-40 font-bold">
											${(act.whishper_usage_logs?.[0]?.cost || 0).toFixed(4)}
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>

				<!-- Management Actions -->
				<div class="border-t border-base-content/5 pt-8 mt-12 mb-4">
					<h3 class="text-xl font-black mb-6">Management Decisions</h3>
					<div class="flex flex-wrap gap-4">
						<button
							on:click={() => toggleStatus(selectedUser)}
							class="btn flex-1 rounded-2xl h-16 {selectedUser.status === 'active'
								? 'btn-outline btn-error'
								: 'btn-success shadow-lg shadow-success/20 animate-pulse-subtle'}"
						>
							<div class="flex flex-col items-center">
								<span class="font-black uppercase tracking-widest"
									>{selectedUser.status === 'active' ? 'Pause Account' : 'Activate Access'}</span
								>
								<span class="text-[9px] opacity-60 normal-case font-medium"
									>{selectedUser.status === 'active'
										? 'Temporarily restrict usage'
										: 'Grant full access to services'}</span
								>
							</div>
						</button>
						<button
							on:click={() => deleteUser(selectedUser)}
							class="btn btn-outline btn-ghost border-error/20 hover:bg-error hover:text-error-content hover:border-error flex-1 rounded-2xl h-16 transition-all"
						>
							<div class="flex flex-col items-center">
								<span class="font-black uppercase tracking-widest">Delete Identity</span>
								<span class="text-[9px] opacity-60 normal-case font-medium"
									>Clear all user records permanentely</span
								>
							</div>
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	:global(.table tr:hover td) {
		background-color: transparent !important;
	}
	.table :where(thead, tfoot) :where(th, td) {
		background-color: transparent;
	}
	.animate-pulse-subtle {
		animation: pulse-subtle 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
	@keyframes pulse-subtle {
		0%,
		100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.95;
			transform: scale(1.01);
		}
	}
</style>
