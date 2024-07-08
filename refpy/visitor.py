

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar


if TYPE_CHECKING:
    
    import refpy.nodes


T = TypeVar("T")

class ExpressionVisitor(Generic[T]):
    @abstractmethod
    def visit_int_expr(self, o: refpy.nodes.IntExpr) -> T:
        pass

    @abstractmethod
    def visit_str_expr(self, o: refpy.nodes.StrExpr) -> T:
        pass
    @abstractmethod
    def visit_float_expr(self, o: refpy.nodes.FloatExpr) -> T:
        pass

    @abstractmethod
    def visit_ellipsis(self, o: refpy.nodes.EllipsisExpr) -> T:
        pass

    @abstractmethod
    def visit_name_expr(self, o: refpy.nodes.NameExpr) -> T:
        pass

    @abstractmethod
    def visit_member_expr(self, o: refpy.nodes.MemberExpr) -> T:
        pass


    @abstractmethod
    def visit_call_expr(self, o: refpy.nodes.CallExpr) -> T:
        pass

    @abstractmethod
    def visit_op_expr(self, o: refpy.nodes.OpExpr) -> T:
        pass

    @abstractmethod
    def visit_comparison_expr(self, o: refpy.nodes.ComparisonExpr) -> T:
        pass

    @abstractmethod
    def visit_super_expr(self, o: refpy.nodes.SuperExpr) -> T:
        pass

    @abstractmethod
    def visit_unary_expr(self, o: refpy.nodes.UnaryExpr) -> T:
        pass

    @abstractmethod
    def visit_list_expr(self, o: refpy.nodes.ListExpr) -> T:
        pass

    @abstractmethod
    def visit_dict_expr(self, o: refpy.nodes.DictExpr) -> T:
        pass

    @abstractmethod
    def visit_tuple_expr(self, o: refpy.nodes.TupleExpr) -> T:
        pass

    @abstractmethod
    def visit_set_expr(self, o: refpy.nodes.SetExpr) -> T:
        pass

    @abstractmethod
    def visit_index_expr(self, o: refpy.nodes.IndexExpr) -> T:
        pass

    @abstractmethod
    def visit_conditional_expr(self, o: refpy.nodes.ConditionalExpr) -> T:
        pass
class StatementVisitor(Generic[T]):
    

    @abstractmethod
    def visit_assignment_stmt(self, o: refpy.nodes.AssignmentStmt) -> T:
        pass


    @abstractmethod
    def visit_func_def(self, o: refpy.nodes.FuncDef) -> T:
        pass

    @abstractmethod
    def visit_class_def(self, o: refpy.nodes.ClassDef) -> T:
        pass

    

    @abstractmethod
    def visit_import(self, o: refpy.nodes.Import) -> T:
        pass

    @abstractmethod
    def visit_import_from(self, o: refpy.nodes.ImportFrom) -> T:
        pass

    @abstractmethod
    def visit_import_all(self, o: refpy.nodes.ImportAll) -> T:
        pass

    

    @abstractmethod
    def visit_block(self, o: refpy.nodes.Block) -> T:
        pass

    @abstractmethod
    def visit_expression_stmt(self, o: refpy.nodes.ExpressionStmt) -> T:
        pass

    @abstractmethod
    def visit_while_stmt(self, o: refpy.nodes.WhileStmt) -> T:
        pass

    @abstractmethod
    def visit_return_stmt(self, o: refpy.nodes.ReturnStmt) -> T:
        pass

    @abstractmethod
    def visit_assert_stmt(self, o: refpy.nodes.AssertStmt) -> T:
        pass

    @abstractmethod
    def visit_if_stmt(self, o: refpy.nodes.IfStmt) -> T:
        pass

    @abstractmethod
    def visit_break_stmt(self, o: refpy.nodes.BreakStmt) -> T:
        pass

    @abstractmethod
    def visit_continue_stmt(self, o: refpy.nodes.ContinueStmt) -> T:
        pass

    @abstractmethod
    def visit_pass_stmt(self, o: refpy.nodes.PassStmt) -> T:
        pass

# mypy: ignore_errors
# ignore empty body error
class NodeVisitor(Generic[T], ExpressionVisitor[T], StatementVisitor[T]):

    def visit_refpy_file(self, o: refpy.nodes.RefpyFile) -> T:
        pass

    
    def visit_import(self, o: refpy.nodes.Import) -> T:
        pass

    def visit_import_from(self, o: refpy.nodes.ImportFrom) -> T:
        pass

    def visit_import_all(self, o: refpy.nodes.ImportAll) -> T:
        pass

    def visit_var(self, o: refpy.nodes.Var) -> T:
        pass


    def visit_func_def(self, o: refpy.nodes.FuncDef) -> T:
        pass

    def visit_class_def(self, o: refpy.nodes.ClassDef) -> T:
        pass
    

    def visit_block(self, o: refpy.nodes.Block) -> T:
        pass

    def visit_expression_stmt(self, o: refpy.nodes.ExpressionStmt) -> T:
        pass

    def visit_assignment_stmt(self, o: refpy.nodes.AssignmentStmt) -> T:
        pass

    def visit_while_stmt(self, o: refpy.nodes.WhileStmt) -> T:
        pass


    def visit_return_stmt(self, o: refpy.nodes.ReturnStmt) -> T:
        pass

    def visit_assert_stmt(self, o: refpy.nodes.AssertStmt) -> T:
        pass


    def visit_if_stmt(self, o: refpy.nodes.IfStmt) -> T:
        pass

    def visit_break_stmt(self, o: refpy.nodes.BreakStmt) -> T:
        pass

    def visit_continue_stmt(self, o: refpy.nodes.ContinueStmt) -> T:
        pass

    def visit_pass_stmt(self, o: refpy.nodes.PassStmt) -> T:
        pass
    

    def visit_int_expr(self, o: refpy.nodes.IntExpr) -> T:
        pass

    def visit_str_expr(self, o: refpy.nodes.StrExpr) -> T:
        pass

    def visit_float_expr(self, o: refpy.nodes.FloatExpr) -> T:
        pass

    def visit_ellipsis(self, o: refpy.nodes.EllipsisExpr) -> T:
        pass

    def visit_name_expr(self, o: refpy.nodes.NameExpr) -> T:
        pass

    def visit_member_expr(self, o: refpy.nodes.MemberExpr) -> T:
        pass

    def visit_call_expr(self, o: refpy.nodes.CallExpr) -> T:
        pass

    def visit_op_expr(self, o: refpy.nodes.OpExpr) -> T:
        pass

    def visit_comparison_expr(self, o: refpy.nodes.ComparisonExpr) -> T:
        pass

    def visit_super_expr(self, o: refpy.nodes.SuperExpr) -> T:
        pass

    def visit_unary_expr(self, o: refpy.nodes.UnaryExpr) -> T:
        pass

    def visit_list_expr(self, o: refpy.nodes.ListExpr) -> T:
        pass

    def visit_dict_expr(self, o: refpy.nodes.DictExpr) -> T:
        pass

    def visit_tuple_expr(self, o: refpy.nodes.TupleExpr) -> T:
        pass

    def visit_set_expr(self, o: refpy.nodes.SetExpr) -> T:
        pass

    def visit_index_expr(self, o: refpy.nodes.IndexExpr) -> T:
        pass

    def visit_conditional_expr(self, o: refpy.nodes.ConditionalExpr) -> T:
        pass