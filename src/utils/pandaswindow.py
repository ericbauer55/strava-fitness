import pandas as pd
from typing import Callable, Dict, List, Optional, Any
# Type Aliases
Dataframe = pd.DataFrame
Transform = Callable[[Dataframe], Dataframe] # f: Dataframe -> Dataframe
Partition = Dict[Any, Dataframe]

class PandasWindow():
    def __init__(self, partition_by:str, order_by:str) -> None:
        """
        Inputs:
        @partition_by = the name of the column to partition the dataframes by
        @order_by = the name of the column to sort the recombines dataframes on
        """
        self.partition_by = partition_by
        self.order_by = order_by
    
    def apply_func(self, df:Dataframe, func:Transform) -> Dataframe:
        # PARTITION
        partition_dict = self._partition_dataframe(df)
        # APPLY
        partition_dict = self._apply_to_partitions(partition_dict=partition_dict, func=func)
        # COMBINE
        df = self._combine_partitions(partition_dict=partition_dict)
        return df
    
    def _partition_dataframe(self, df:Dataframe) -> Partition:
        df_grouped = df.groupby(self.partition_by)
        groups = df_grouped.groups.keys()
        # build the partitioned dataframe where key=categories of @on_column
        # and the values are the dataframes where @on_column == category_i
        partition_dict = {group:df_grouped.get_group(group) for group in groups}
        return partition_dict
    
    @staticmethod
    def _apply_to_partitions(partition_dict:Partition, func:Transform) -> Partition:
        for partition in partition_dict.keys():
            # For each group/partition of the partition
            partition_dict[partition] = func(partition_dict[partition])
        return partition_dict
    
    def _combine_partitions(self, partition_dict:Partition) -> Dataframe:
        # Gather the various dataframes of each partition
        dataframes = [df_partition for df_partition in partition_dict.values()]
        df = pd.concat(dataframes)
        # sort the rows by @sort_by
        df = df.set_index(self.order_by).sort_index().reset_index()
        return df
        
    