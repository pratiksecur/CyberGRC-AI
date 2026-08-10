import Skeleton from "@/components/ui/Skeleton";

export default function DashboardSkeleton() {

  return (

    <div className="space-y-6">

      {/* Search */}

      <Skeleton className="h-12 w-full" />

      {/* Cards */}

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

        {[1,2,3,4].map((i)=>(
          <Skeleton
            key={i}
            className="h-36"
          />
        ))}

      </div>

      {/* Charts */}

      <div className="grid gap-6 lg:grid-cols-2">

        <Skeleton className="h-80" />

        <Skeleton className="h-80" />

      </div>

      {/* Widgets */}

      <div className="grid gap-6 lg:grid-cols-2">

        <Skeleton className="h-48" />

        <Skeleton className="h-48" />

      </div>

      {/* Table */}

      <Skeleton className="h-72" />

    </div>

  );

}