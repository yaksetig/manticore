from ...core.plugin import Plugin


class CoveragePlugin(Plugin):
    """Collect EVM instruction coverage and execution trace information."""

    def did_evm_execute_instruction_callback(self, state, instruction, arguments, result):
        at_init = state.platform.current_transaction.sort == "CREATE"
        item = (state.platform.current_vm.address, instruction.pc, at_init)

        # Record coverage globally
        with self.manticore.locked_context("evm.coverage", list) as coverage:
            if item not in coverage:
                coverage.append(item)

        # Record per-state execution trace
        state.context.setdefault("evm.trace", []).append(item)
