<script>
	import { supabase } from '$lib/supabase';
	import { onMount } from 'svelte';
	import toast from 'svelte-french-toast';

	let users = [];
	let loading = true;
	let newAdminEmail = '';
	let addingAdmin = false;

	async function fetchData() {
		loading = true;
		try {
			// Fetch Profiles
			const { data: profiles, error: profilesError } = await supabase
				.from('profiles')
				.select('*')
				.order('created_at', { ascending: false });

			if (profilesError) throw profilesError;

			// Fetch Usage Logs
			const { data: logs, error: logsError } = await supabase.from('usage_logs').select('*');

			if (logsError) throw logsError;

			// Aggregate Data
			users = profiles.map((profile) => {
				const userLogs = logs.filter((log) => log.user_id === profile.id);
				const totalSeconds = userLogs.reduce(
					(acc, log) => acc + (log.usage_type === 'transcription_seconds' ? Number(log.amount) : 0),
					0
				);
				const totalCost = userLogs.reduce((acc, log) => acc + Number(log.cost), 0);

				return {
					...profile,
					totalSeconds,
					totalCost,
					usageCount: userLogs.length
				};
			});
		} catch (error) {
			toast.error(error.message);
		} finally {
			loading = false;
		}
	}

	async function handleAddAdmin() {
		if (!newAdminEmail) return;
		addingAdmin = true;
		try {
			// We update by Email. Note: RLS allows admins to update all.
			// However, we need to find the ID first or update by email?
			// Public profiles are viewable, so we can find ID by email.

			const { data: targetProfile, error: searchError } = await supabase
				.from('profiles')
				.select('id')
				.eq('email', newAdminEmail)
				.single();

			if (searchError || !targetProfile) {
				toast.error('User not found. They must sign up first.');
				return;
			}

			const { error } = await supabase
				.from('profiles')
				.update({ role: 'admin' })
				.eq('id', targetProfile.id);

			if (error) throw error;

			toast.success(`${newAdminEmail} is now an admin.`);
			newAdminEmail = '';
			fetchData();
		} catch (error) {
			toast.error(error.message);
		} finally {
			addingAdmin = false;
		}
	}

	onMount(() => {
		fetchData();
	});
</script>

<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
	<div class="stats shadow bg-base-100">
		<div class="stat">
			<div class="stat-title">Total Users</div>
			<div class="stat-value">{users.length}</div>
		</div>
	</div>

	<div class="stats shadow bg-base-100">
		<div class="stat">
			<div class="stat-title">Total Spend (Est.)</div>
			<div class="stat-value text-primary">
				${users.reduce((acc, u) => acc + u.totalCost, 0).toFixed(4)}
			</div>
			<div class="stat-desc">Based on $0.03/hr</div>
		</div>
	</div>

	<div class="stats shadow bg-base-100">
		<div class="stat">
			<div class="stat-title">Total Transcribed</div>
			<div class="stat-value text-secondary text-2xl">
				{(users.reduce((acc, u) => acc + u.totalSeconds, 0) / 3600).toFixed(2)} hrs
			</div>
		</div>
	</div>
</div>

<div class="card bg-base-100 shadow-xl mb-8">
	<div class="card-body">
		<h3 class="card-title mb-4">Add New Admin</h3>
		<div class="flex gap-4 items-end">
			<div class="form-control w-full max-w-md">
				<label class="label">
					<span class="label-text">User Email</span>
				</label>
				<input
					type="email"
					placeholder="user@example.com"
					class="input input-bordered w-full"
					bind:value={newAdminEmail}
				/>
			</div>
			<button class="btn btn-primary" on:click={handleAddAdmin} disabled={addingAdmin}>
				{#if addingAdmin}
					<span class="loading loading-spinner loading-sm" />
				{/if}
				Grant Admin
			</button>
		</div>
		<p class="text-xs opacity-60 mt-2">The user must already be registered in the system.</p>
	</div>
</div>

<div class="card bg-base-100 shadow-xl overflow-x-auto">
	<table class="table table-zebra w-full">
		<thead>
			<tr>
				<th>User</th>
				<th>Role</th>
				<th>Transcriptions</th>
				<th>Total Duration</th>
				<th>Total Cost</th>
				<th>Joined</th>
			</tr>
		</thead>
		<tbody>
			{#each users as user}
				<tr>
					<td>
						<div class="flex items-center space-x-3">
							<div class="avatar placeholder">
								<div class="bg-neutral-focus text-neutral-content rounded-full w-8">
									<span class="text-xs">{user.email?.substring(0, 2).toUpperCase()}</span>
								</div>
							</div>
							<div>
								<div class="font-bold">{user.email}</div>
								<div class="text-sm opacity-50">{user.id}</div>
							</div>
						</div>
					</td>
					<td>
						{#if user.role === 'admin'}
							<span class="badge badge-primary badge-outline">Admin</span>
						{:else}
							<span class="badge badge-ghost badge-outline">User</span>
						{/if}
					</td>
					<td>{user.usageCount}</td>
					<td>{(user.totalSeconds / 60).toFixed(1)} min</td>
					<td class="font-mono text-primary">${user.totalCost.toFixed(4)}</td>
					<td class="text-sm opacity-60">{new Date(user.created_at).toLocaleDateString()}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
