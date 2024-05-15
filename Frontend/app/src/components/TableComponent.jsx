import { useEffect, useMemo, useState } from 'react';
import {
  MaterialReactTable,
  useMaterialReactTable,
} from 'material-react-table';

const TableComponent = (userId) => {
  //data and fetching state
  const [data, setData] = useState([]);
  const [isError, setIsError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefetching, setIsRefetching] = useState(false);
  const [rowCount, setRowCount] = useState(0);

  //table state
  const [columnFilters, setColumnFilters] = useState([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState([]);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  //if you want to avoid useEffect, look at the React Query example instead
  useEffect(() => {
    const fetchData = async () => {
      if (!data.length) {
        setIsLoading(true);
      } else {
        setIsRefetching(true);
      }

      const url = new URL(
        '/api/movies',
        process.env.NODE_ENV === 'production'
          ? 'https://www.material-react-table.com'
          : `${process.env.REACT_APP_BACKEND_URL}`,
      );

      url.searchParams.set('page', `${pagination.pageIndex + 1}`);
      url.searchParams.set('pageSize', `${pagination.pageSize}`);
      try {
        const response = await fetch(url.href,{ method: 'GET', headers: {
          'Authorization': `Bearer ${localStorage.getItem("token")}` 
        }});
        const json = await response.json();
        setData(json);
        
      } catch (error) {
        setIsError(true);
        console.error(error);
        return;
      }
      setIsError(false);
      setIsLoading(false);
      setIsRefetching(false);
    };
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    columnFilters,
    globalFilter,
    pagination.pageIndex,
    pagination.pageSize,
    sorting,
  ]);

  console.log(data)
  const columns = useMemo(
    () => [
    {
      accessorKey: 'title',
      header: 'Title',
    },
      {
        accessorKey: 'cast',
        header: 'CAST',
      },
      {
        accessorKey: 'country',
        header: 'Country',
      },
      {
        accessorKey: 'date_added',
        header: 'Date Added',
      },
      {
        accessorKey: 'createdAt',
        header: 'Added By You',
      },
      {
        accessorKey: 'description',
        header: 'Description',
      },
      {
        accessorKey: 'listed_in',
        header: 'Listed In',
      },
      
      // {
      //   accessorKey: 'cast',
      //   header: 'CAST',
      // },
      //column definitions...
    ],
    [],
  );

  const table = useMaterialReactTable({
    columns,
    data,
    enableRowSelection: true,
    getRowId: (row) => row.phoneNumber,
    initialState: { showColumnFilters: true },
    manualFiltering: true,
    manualPagination: true,
    manualSorting: true,
    muiToolbarAlertBannerProps: isError
      ? {
          color: 'error',
          children: 'Error loading data',
        }
      : undefined,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    onPaginationChange: setPagination,
    onSortingChange: setSorting,
    rowCount,
    state: {
      columnFilters,
      globalFilter,
      isLoading,
      pagination,
      showAlertBanner: isError,
      showProgressBars: isRefetching,
      sorting,
    },
  });

  return <MaterialReactTable table={table} />;
};

export default TableComponent;